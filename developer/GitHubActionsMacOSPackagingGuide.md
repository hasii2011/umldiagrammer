# Automating macOS Application Build, Signing, and Notarization with GitHub Actions

This guide details how to automate the build, signing, packaging, notarization, and stapling workflow for **UmlDiagrammer** in a GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`).

---

## 1. Overview and Architecture

The local build and packaging workflow consists of:
1. Building the `.app` bundle via `py2app` with Python 3.13.
2. Patching binary Mach-O build versions with `/usr/bin/vtool`.
3. Fixing dynamic library linkage for Pillow (`liblzma.5.dylib` from Homebrew `xz`).
4. Signing zip archives and bundle contents with `py2AppSign`.
5. Creating and signing the disk image (`.dmg`) using `dmgTool`.
6. Notarizing with Apple via `xcrun notarytool`.
7. Stapling notarization tickets to the `.dmg` using `xcrun stapler`.
8. Verifying Gatekeeper acceptance with `spctl --assess`.

GitHub Actions provides hosted **macOS runners** (`macos-14` / Apple Silicon) that have Xcode command-line tools (`vtool`, `codesign`, `xcrun notarytool`, `xcrun stapler`, `spctl`) and Homebrew pre-installed. By securely passing your code signing certificate and Apple credentials via **GitHub Repository Secrets**, the entire process can run automatically on pushes and release tags.

---

## 2. Exporting Your Apple Developer ID Certificate on macOS

To sign your application on an ephemeral GitHub runner, you must export your **Developer ID Application** certificate and private key into an encrypted `.p12` (Personal Information Exchange) file.

### Step-by-Step Instructions:

1. **Launch Keychain Access:**
   * Open **Finder** -> **Applications** -> **Utilities** -> **Keychain Access** (or press `Cmd + Space`, type `Keychain Access`, and press `Enter`).

2. **Select the Login Keychain and Certificates Category:**
   * In the Keychain Access sidebar under **Default Keychains**, click **login**.
   * Under the **Category** tab or filter bar, select **My Certificates** (or **Certificates**).

3. **Locate Your Developer ID Certificate:**
   * Look for the certificate named:
     ```text
     Developer ID Application: <Your Name / Company Name> (<Team ID>)
     ```
     *(Example: `Developer ID Application: Humberto Sanchez II (ABC123XYZ4)`)*
   * Click the disclosure triangle `>` next to the certificate name to verify that your private key is nested underneath it.

4. **Export the Certificate and Private Key:**
   * Highlight the **Developer ID Application** certificate (both the certificate and its nested private key will be included).
   * Right-click (or control-click) on the item and select:
     ```text
     Export "Developer ID Application: ..."
     ```
   * In the **Save As** dialog:
     * **File Name:** `DeveloperID.p12`
     * **Where:** Save to a temporary local folder (e.g. `~/Desktop` or `~/Downloads`).
     * **File Format:** Ensure **Personal Information Exchange (.p12)** is selected in the dropdown menu.
     * Click **Save**.

5. **Set an Export Password:**
   * A prompt will appear asking for a password to protect the exported items.
   * Enter a strong password and verify it. **Save this password**; you will need it for the `MACOS_CERTIFICATE_PASSWORD` secret.
   * Click **OK**.
   * macOS will prompt for your Mac user login password to authorize exporting the private key from your keychain. Enter your credentials and click **Allow** (or **Always Allow**).

6. **Base64-Encode the `.p12` File:**
   * Open **Terminal** and navigate to where you saved the file:
     ```bash
     base64 -i ~/Desktop/DeveloperID.p12 | pbcopy
     ```
   * The base64-encoded string is now copied directly to your macOS clipboard.
   * **Security Best Practice:** Once copied to GitHub Secrets, permanently delete `~/Desktop/DeveloperID.p12` from your machine.

---

## 3. Creating App Store Connect API Key for Notarytool

Apple's `xcrun notarytool` on CI systems authenticates using an **App Store Connect API Key** instead of an interactive Apple ID and app-specific password.

### Step-by-Step Instructions:

1. Log into [App Store Connect](https://appstoreconnect.apple.com/).
2. Navigate to **Users and Access** -> **Integrations** (or **Keys**) -> **App Store Connect API**.
3. Click the **+** (Generate API Key) button:
   * **Name:** `GitHub Actions Notary Key`
   * **Access:** Select `Developer` (or `Admin`).
4. Note the following values:
   * **Key ID:** A 10-character string (e.g., `2X9R4HXF34`).
   * **Issuer ID:** A UUID found at the top of the Keys page (e.g., `57246542-96fe-1a63-e053-0824d011072a`).
5. Click **Download API Key** to download the `AuthKey_<KeyID>.p8` file. *(Note: Apple only allows downloading this key once).*
6. Base64-encode the `.p8` file to your clipboard:
   ```bash
   base64 -i ~/Downloads/AuthKey_<KeyID>.p8 | pbcopy
   ```

---

## 4. Configuring GitHub Repository Secrets

In your GitHub repository:
1. Go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret** for each of the following:

| Secret Name | Description | Example / Source |
| :--- | :--- | :--- |
| `MACOS_CERTIFICATE_P12_BASE64` | Base64-encoded content of your `DeveloperID.p12` file | Output from `base64 -i DeveloperID.p12` |
| `MACOS_CERTIFICATE_PASSWORD` | The password you set when exporting the `.p12` file | Plaintext export password |
| `KEYCHAIN_PASSWORD` | A temporary password used to create the ephemeral CI keychain | Any random alphanumeric string |
| `CODE_SIGNING_IDENTITY` | The exact Common Name of your certificate | `Developer ID Application: Humberto Sanchez II (TEAMID)` |
| `APPLE_API_KEY_BASE64` | Base64-encoded content of your `AuthKey_<KeyID>.p8` file | Output from `base64 -i AuthKey_XXXXX.p8` |
| `APPLE_API_KEY_ID` | The 10-character Key ID from App Store Connect | e.g. `2X9R4HXF34` |
| `APPLE_API_ISSUER` | The Issuer ID UUID from App Store Connect | e.g. `57246542-96fe-1a63-e053-0824d011072a` |

---

## 5. Handling Dynamic Library Linkage (`liblzma.5.dylib`)

In virtual environments, py2app packages the PIL (Pillow) library which depends on `liblzma.5.dylib`. In GitHub Actions, Homebrew provides `xz`. The runner script copies this library into the active Python environment's site-packages:

```bash
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
mkdir -p "${SITE_PACKAGES}/PIL/.dylibs"
cp $(brew --prefix xz)/lib/liblzma.5.dylib "${SITE_PACKAGES}/PIL/.dylibs/"
```

---

## 6. Complete GitHub Actions Workflow (`.github/workflows/ci.yml`)

Create the workflow file at `.github/workflows/ci.yml`:

```yaml
name: CI & macOS Release Packaging

on:
  push:
    branches: [ 'master', 'Issue-*' ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ 'master' ]

jobs:
  build-macos:
    name: Build, Sign & Notarize macOS App
    runs-on: macos-14
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.13']

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install System Dependencies
        run: |
          brew install xz
          python -m pip install --upgrade pip

      - name: Install Project Dependencies
        run: |
          pip install -r requirements.txt
          pip install py2appsigner

      - name: Fix PIL liblzma Dynamic Library
        run: |
          SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
          mkdir -p "${SITE_PACKAGES}/PIL/.dylibs"
          cp $(brew --prefix xz)/lib/liblzma.5.dylib "${SITE_PACKAGES}/PIL/.dylibs/"

      - name: Run Type Checks (mypy)
        run: |
          mypy --config-file .mypi.ini --check-untyped-defs src

      - name: Import Apple Code Signing Certificate
        if: ${{ secrets.MACOS_CERTIFICATE_P12_BASE64 != '' }}
        env:
          CERTIFICATE_P12_BASE64: ${{ secrets.MACOS_CERTIFICATE_P12_BASE64 }}
          CERTIFICATE_PASSWORD: ${{ secrets.MACOS_CERTIFICATE_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          KEYCHAIN_PATH=$RUNNER_TEMP/build.keychain
          echo -n "$CERTIFICATE_P12_BASE64" | base64 --decode -o $RUNNER_TEMP/certificate.p12

          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

          security import $RUNNER_TEMP/certificate.p12 -P "$CERTIFICATE_PASSWORD" -A -t cert -f pkcs12 -k $KEYCHAIN_PATH
          security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security list-keychain -d user -s $KEYCHAIN_PATH $(security list-keychains -d user | tr -d '"')

      - name: Configure Notarytool Credentials Profile
        if: ${{ secrets.APPLE_API_KEY_BASE64 != '' }}
        env:
          KEY_BASE64: ${{ secrets.APPLE_API_KEY_BASE64 }}
          KEY_ID: ${{ secrets.APPLE_API_KEY_ID }}
          ISSUER: ${{ secrets.APPLE_API_ISSUER }}
        run: |
          echo -n "$KEY_BASE64" | base64 --decode -o $RUNNER_TEMP/AuthKey.p8
          xcrun notarytool store-credentials "NOTARY_TOOL_APP_ID" \
            --key "$RUNNER_TEMP/AuthKey.p8" \
            --key-id "$KEY_ID" \
            --issuer "$ISSUER" \
            --keychain $RUNNER_TEMP/build.keychain

      - name: Build py2app Bundle
        run: |
          rm -rf build dist src/UmlDiagrammer.egg-info UmlDiagrammer.egg-info
          python -O setup.py py2app --iconfile src/umldiagrammer/resources/icons/umldiagrammer.icns
          vtool -set-build-version 1 26.0 26.1 -replace -output dist/UmlDiagrammer.app/Contents/MacOS/UmlDiagrammer dist/UmlDiagrammer.app/Contents/MacOS/UmlDiagrammer

      - name: Sign App Bundle and Create DMG
        env:
          IDENTITY: ${{ secrets.CODE_SIGNING_IDENTITY }}
          PROJECTS_BASE: ${{ github.workspace }}/..
          PROJECT: ${{ github.event.repository.name }}
        run: |
          if [ -n "$IDENTITY" ]; then
            py2AppSign -p 3.13 -d umldiagrammer -a UmlDiagrammer zipSign --delete-part-files
            py2AppSign -p 3.13 -d umldiagrammer -a UmlDiagrammer appSign
            dmgTool -a UmlDiagrammer -d dist createDmg
            dmgTool -a UmlDiagrammer -d dist signDmg
          else
            echo "Signing identity not found. Creating unsigned/ad-hoc bundle for CI validation..."
            codesign --force --deep --sign - dist/UmlDiagrammer.app
            dmgTool -a UmlDiagrammer -d dist createDmg
          fi

      - name: Notarize, Staple and Verify DMG
        if: ${{ secrets.APPLE_API_KEY_BASE64 != '' }}
        run: |
          xcrun notarytool submit dist/UmlDiagrammer.dmg --keychain-profile NOTARY_TOOL_APP_ID --keychain $RUNNER_TEMP/build.keychain --wait
          xcrun stapler staple dist/UmlDiagrammer.dmg
          spctl --assess --type install --verbose dist/UmlDiagrammer.dmg

      - name: Upload DMG Artifact
        uses: actions/upload-artifact@v4
        with:
          name: UmlDiagrammer-macOS-Installer
          path: dist/UmlDiagrammer.dmg
          retention-days: 14

      - name: Clean Up Keychain
        if: always()
        run: |
          security delete-keychain $RUNNER_TEMP/build.keychain 2>/dev/null || true
```
