#!/usr/bin/env bash
#
#
#  The generated .icns file is copied to src/umldiagrammer/resources/img/umldiagrammer.icns
#
#
ICON_DIR="../../src/umldiagrammer/resources/icons/"
IMAGES="${ICON_DIR}/sourceimages/"
ICON_IMAGE="${IMAGES}/umldiagrammer-logo.png"

ICON_SET_DIR="umldiagrammer.iconset"
JUNK_OUTPUT='throwaway.txt'

rm -rf ${ICON_SET_DIR}
mkdir ${ICON_SET_DIR}

echo 'Start icon creation'
sips -z 16 16     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_16x16.png      > ${JUNK_OUTPUT}
sips -z 32 32     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_16x16@2x.png   > ${JUNK_OUTPUT}

sips -z 32 32     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_32x32.png      > ${JUNK_OUTPUT}
sips -z 64 64     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_32x32@2x.png   > ${JUNK_OUTPUT}

sips -z 128 128 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_128x128.png      > ${JUNK_OUTPUT}
sips -z 256 256 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_128x128@2x.png   > ${JUNK_OUTPUT}

sips -z 256 256 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_256x256.png      > ${JUNK_OUTPUT}
sips -z 512 512 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_256x256@2x.png   > ${JUNK_OUTPUT}

sips -z 512 512 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_512x512.png      > ${JUNK_OUTPUT}

cp ${ICON_IMAGE} ${ICON_SET_DIR}/icon_512x512@2x.png

echo 'Base icons created'

iconutil -c icns ${ICON_SET_DIR}
echo 'Apple icon set created'

cp -p umldiagrammer.icns ${ICON_DIR}
echo 'Copied to developer resource directory'


echo 'Cleaning up working files'
rm -rf ${ICON_SET_DIR}
rm umldiagrammer.icns
rm ${JUNK_OUTPUT}
