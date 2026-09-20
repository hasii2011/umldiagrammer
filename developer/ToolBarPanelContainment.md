
# UML Diagrammer - ToolBar Panel Containment & Layout Architecture

This document details the panel containment hierarchy and layout management used to host and position the custom `AuiToolBar` within `UmlDiagrammerAppFrame`.

---

## 1. Complete Panel Containment Hierarchy Overview

The application frame (`UmlDiagrammerAppFrame`) inherits from `wx.lib.sized_controls.SizedFrame`. Instead of docking the toolbar into native wxFrame toolbar slots via `SetToolBar()`, the toolbar is hosted inside the frame's root `SizedPanel` (`contentsPane`), functioning as a managed sibling to `UmlNotebook`.

```mermaid
flowchart TD
    classDef tbHighlight fill:#ffe082,stroke:#f57c00,stroke-width:3px,font-weight:bold,color:#000
    classDef panelStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef frameStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef leafStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000

    AppFrame["UmlDiagrammerAppFrame (SizedFrame)"]:::frameStyle
    MenuBar["wx.MenuBar\n(File, Edit, Extensions, Help)"]:::leafStyle
    StatusBar["wx.StatusBar\n(Single/Multi-pane status)"]:::leafStyle
    ContentsPane["Contents Pane: SizedPanel\n(expand=True, proportion=1)"]:::panelStyle

    AppFrame --> MenuBar
    AppFrame --> StatusBar
    AppFrame --> ContentsPane

    ToolBar["★ wx.aui.AuiToolBar (self._tb) ★\n(Managed by ToolBarCreator)\nproportion=0, expand=True\nAUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW"]:::tbHighlight
    Notebook["UmlNotebook (wx.Notebook)\n(self._umlNotebook)\nproportion=1, expand=True\nTab style via DiagrammerPreferences"]:::panelStyle

    ContentsPane --> ToolBar
    ContentsPane --> Notebook

    ProjectPanel["UmlProjectPanel (wx.SplitterWindow)\n(One per project tab in UmlNotebook)"]:::panelStyle
    Notebook --> ProjectPanel

    ProjectTree["UmlProjectTree (wx.TreeCtrl)\n(Left Pane, sash-split)\nProject & Diagram Tree"]:::leafStyle
    DiagramManager["UmlDiagramManager (wx.Simplebook)\n(Right Pane, sash-split)\nDiagram Switcher"]:::panelStyle

    ProjectPanel --> ProjectTree
    ProjectPanel --> DiagramManager

    ClassFrame["ClassDiagramFrame\n(ShapeCanvas / ScrolledWindow)"]:::leafStyle
    UseCaseFrame["UseCaseDiagramFrame\n(ShapeCanvas / ScrolledWindow)"]:::leafStyle
    SeqFrame["SequenceDiagramFrame\n(ShapeCanvas / ScrolledWindow)"]:::leafStyle

    DiagramManager --> ClassFrame
    DiagramManager --> UseCaseFrame
    DiagramManager --> SeqFrame
```

---

## 2. Dynamic Sizer Configuration & Containment by Position

The root container (`contentsPane: SizedPanel`) dynamically configures its internal `wx.BoxSizer` based on `preferences.toolBarPosition`.

| ToolBar Position | Sizer Orientation              | Toolbar Style Flags                                          | Sizer Slot 0 (First)      | Sizer Slot 1 (Second)     | Docking Method              |
| :--------------- | :----------------------------- | :----------------------------------------------------------- | :------------------------ | :------------------------ | :-------------------------- |
| **TOP**          | `vertical` (`wx.VERTICAL`)     | `AUI_TB_DEFAULT_STYLE \| AUI_TB_OVERFLOW`                    | **`AuiToolBar`** (prop=0) | `UmlNotebook` (prop=1)    | Natural instantiation order |
| **BOTTOM**       | `vertical` (`wx.VERTICAL`)     | `AUI_TB_DEFAULT_STYLE \| AUI_TB_OVERFLOW`                    | `UmlNotebook` (prop=1)    | **`AuiToolBar`** (prop=0) | `_manuallyDockToolBar()`    |
| **LEFT**         | `horizontal` (`wx.HORIZONTAL`) | `AUI_TB_DEFAULT_STYLE \| AUI_TB_OVERFLOW \| AUI_TB_VERTICAL` | **`AuiToolBar`** (prop=0) | `UmlNotebook` (prop=1)    | Natural instantiation order |
| **RIGHT**        | `horizontal` (`wx.HORIZONTAL`) | `AUI_TB_DEFAULT_STYLE \| AUI_TB_OVERFLOW \| AUI_TB_VERTICAL` | `UmlNotebook` (prop=1)    | **`AuiToolBar`** (prop=0) | `_manuallyDockToolBar()`    |

---

## 3. Position 1: ToolBar Position = TOP

In the **TOP** configuration:
* `contentsPane` uses a `vertical` sizer.
* The highlighted `AuiToolBar` sits in **Sizer Slot 0** (top), while `UmlNotebook` occupies **Sizer Slot 1** (expanding below it).

### Hierarchy Diagram (TOP Position)

```mermaid
flowchart TD
    classDef tbHighlight fill:#ffe082,stroke:#f57c00,stroke-width:3px,font-weight:bold,color:#000
    classDef panelStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef frameStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef leafStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000

    AppFrame["UmlDiagrammerAppFrame (SizedFrame)"]:::frameStyle
    MenuBar["wx.MenuBar\n(Native Frame Menu)"]:::leafStyle
    StatusBar["wx.StatusBar\n(Native Frame Status)"]:::leafStyle
    ContentsPane["contentsPane: SizedPanel\n(expand=True, proportion=1)\n[Sizer: vertical]"]:::panelStyle

    AppFrame --> MenuBar
    AppFrame --> ContentsPane
    AppFrame --> StatusBar

    ToolBar["★ SIZER SLOT 0 (TOP DOCKED) ★\nwx.aui.AuiToolBar (self._tb)\nHorizontal | prop=0, expand=True\nstyle: AUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW"]:::tbHighlight
    Notebook["SIZER SLOT 1 (EXPANDING WORKSPACE)\nUmlNotebook (self._umlNotebook)\nprop=1, expand=True"]:::panelStyle

    ContentsPane -->|Slot 0: Top Edge| ToolBar
    ContentsPane -->|Slot 1: Below Toolbar| Notebook

    ProjectPanel["UmlProjectPanel (wx.SplitterWindow)\n(Per Project Tab)"]:::panelStyle
    Notebook --> ProjectPanel

    ProjectTree["UmlProjectTree (wx.TreeCtrl)\nLeft Pane (Tree Browser)"]:::leafStyle
    DiagramManager["UmlDiagramManager (wx.Simplebook)\nRight Pane (Diagram Switcher)"]:::panelStyle

    ProjectPanel -->|Split Left| ProjectTree
    ProjectPanel -->|Split Right| DiagramManager

    DiagramFrame["Active DiagramFrame (ShapeCanvas)\n(ClassDiagramFrame / UseCase / Sequence)"]:::leafStyle
    DiagramManager -->|Active Page| DiagramFrame
```

### Visual Layout Table (TOP)

| Frame Layer            | Component                             | Sizer Slot & Props          | Visual Layout & Role                                            |
| :--------------------- | :------------------------------------ | :-------------------------- | :-------------------------------------------------------------- |
| **Frame Top**          | `wx.MenuBar`                          | Native Frame Menu           | `File` \| `Edit` \| `Extensions` \| `Help`                      |
| **Slot 0 (Top)**       | **`AuiToolBar`** (`self._tb`)         | `prop=0, expand=True`       | `[★ Horizontal ToolBar ★] [>> Overflow Popup]`                  |
| **Slot 1 (Workspace)** | `UmlNotebook` (`self._umlNotebook`)   | `prop=1, expand=True`       | Tabbed projects container (`[Project 1 Tab *] [Project 2 Tab]`) |
| ↳ *Left Splitter*      | `UmlProjectTree` (`wx.TreeCtrl`)      | `SplitterWindow` Left Pane  | Project & diagrams hierarchy tree browser                       |
| ↳ *Right Splitter*     | `UmlDiagramManager` (`wx.Simplebook`) | `SplitterWindow` Right Pane | Active `DiagramFrame` (`ShapeCanvas` drawing surface)           |
| **Frame Bottom**       | `wx.StatusBar`                        | Native Frame Status         | Multi-pane application status and tool hints                    |

---

## 4. Position 2: ToolBar Position = BOTTOM

In the **BOTTOM** configuration:
* `contentsPane` uses a `vertical` sizer.
* `UmlNotebook` occupies **Sizer Slot 0** (upper workspace).
* When `UmlNotebook` is created, `_manuallyDockToolBar()` detaches `self._tb` and appends it at **Sizer Slot 1** (bottom edge).

### Hierarchy Diagram (BOTTOM Position)

```mermaid
flowchart TD
    classDef tbHighlight fill:#ffe082,stroke:#f57c00,stroke-width:3px,font-weight:bold,color:#000
    classDef panelStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef frameStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef leafStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000

    AppFrame["UmlDiagrammerAppFrame (SizedFrame)"]:::frameStyle
    MenuBar["wx.MenuBar\n(Native Frame Menu)"]:::leafStyle
    StatusBar["wx.StatusBar\n(Native Frame Status)"]:::leafStyle
    ContentsPane["contentsPane: SizedPanel\n(expand=True, proportion=1)\n[Sizer: vertical]"]:::panelStyle

    AppFrame --> MenuBar
    AppFrame --> ContentsPane
    AppFrame --> StatusBar

    Notebook["SIZER SLOT 0 (UPPER WORKSPACE)\nUmlNotebook (self._umlNotebook)\nprop=1, expand=True"]:::panelStyle
    ToolBar["★ SIZER SLOT 1 (BOTTOM DOCKED) ★\nwx.aui.AuiToolBar (self._tb)\nHorizontal | prop=0, expand=True\nstyle: AUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW\n(Detached & Re-added via _manuallyDockToolBar)"]:::tbHighlight

    ContentsPane -->|Slot 0: Upper Area| Notebook
    ContentsPane -->|Slot 1: Trailing Bottom Edge| ToolBar

    ProjectPanel["UmlProjectPanel (wx.SplitterWindow)\n(Per Project Tab)"]:::panelStyle
    Notebook --> ProjectPanel

    ProjectTree["UmlProjectTree (wx.TreeCtrl)\nLeft Pane (Tree Browser)"]:::leafStyle
    DiagramManager["UmlDiagramManager (wx.Simplebook)\nRight Pane (Diagram Switcher)"]:::panelStyle

    ProjectPanel -->|Split Left| ProjectTree
    ProjectPanel -->|Split Right| DiagramManager

    DiagramFrame["Active DiagramFrame (ShapeCanvas)\n(ClassDiagramFrame / UseCase / Sequence)"]:::leafStyle
    DiagramManager -->|Active Page| DiagramFrame
```

### Visual Layout Table (BOTTOM)

| Frame Layer            | Component                             | Sizer Slot & Props          | Visual Layout & Role                                                        |
| :--------------------- | :------------------------------------ | :-------------------------- | :-------------------------------------------------------------------------- |
| **Frame Top**          | `wx.MenuBar`                          | Native Frame Menu           | `File` \| `Edit` \| `Extensions` \| `Help`                                  |
| **Slot 0 (Workspace)** | `UmlNotebook` (`self._umlNotebook`)   | `prop=1, expand=True`       | Upper workspace; tabbed projects container                                  |
| ↳ *Left Splitter*      | `UmlProjectTree` (`wx.TreeCtrl`)      | `SplitterWindow` Left Pane  | Project & diagrams hierarchy tree browser                                   |
| ↳ *Right Splitter*     | `UmlDiagramManager` (`wx.Simplebook`) | `SplitterWindow` Right Pane | Active `DiagramFrame` (`ShapeCanvas` drawing surface)                       |
| **Slot 1 (Bottom)**    | **`AuiToolBar`** (`self._tb`)         | `prop=0, expand=True`       | `[★ Horizontal ToolBar ★] [>> Overflow Popup]` (via `_manuallyDockToolBar`) |
| **Frame Bottom**       | `wx.StatusBar`                        | Native Frame Status         | Multi-pane application status and tool hints                                |

---

## 5. Position 3: ToolBar Position = LEFT

In the **LEFT** configuration:
* `contentsPane` uses a `horizontal` sizer via `sizedPanel.SetSizerType('horizontal')`.
* `ToolBarCreator` sets the style flag `AUI_TB_VERTICAL`.
* The highlighted `AuiToolBar` sits in **Sizer Slot 0** (left column), and `UmlNotebook` occupies **Sizer Slot 1** (expanding across the remaining width to the right).

### Hierarchy Diagram (LEFT Position)

```mermaid
flowchart TD
    classDef tbHighlight fill:#ffe082,stroke:#f57c00,stroke-width:3px,font-weight:bold,color:#000
    classDef panelStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef frameStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef leafStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000

    AppFrame["UmlDiagrammerAppFrame (SizedFrame)"]:::frameStyle
    MenuBar["wx.MenuBar\n(Native Frame Menu)"]:::leafStyle
    StatusBar["wx.StatusBar\n(Native Frame Status)"]:::leafStyle
    ContentsPane["contentsPane: SizedPanel\n(expand=True, proportion=1)\n[Sizer: horizontal]"]:::panelStyle

    AppFrame --> MenuBar
    AppFrame --> ContentsPane
    AppFrame --> StatusBar

    ToolBar["★ SIZER SLOT 0 (LEFT DOCKED) ★\nwx.aui.AuiToolBar (self._tb)\nVertical | prop=0, expand=True\nstyle: AUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW | AUI_TB_VERTICAL"]:::tbHighlight
    Notebook["SIZER SLOT 1 (EXPANDING WORKSPACE)\nUmlNotebook (self._umlNotebook)\nprop=1, expand=True"]:::panelStyle

    ContentsPane -->|Slot 0: Left Column| ToolBar
    ContentsPane -->|Slot 1: Right Fill| Notebook

    ProjectPanel["UmlProjectPanel (wx.SplitterWindow)\n(Per Project Tab)"]:::panelStyle
    Notebook --> ProjectPanel

    ProjectTree["UmlProjectTree (wx.TreeCtrl)\nLeft Pane (Tree Browser)"]:::leafStyle
    DiagramManager["UmlDiagramManager (wx.Simplebook)\nRight Pane (Diagram Switcher)"]:::panelStyle

    ProjectPanel -->|Split Left| ProjectTree
    ProjectPanel -->|Split Right| DiagramManager

    DiagramFrame["Active DiagramFrame (ShapeCanvas)\n(ClassDiagramFrame / UseCase / Sequence)"]:::leafStyle
    DiagramManager -->|Active Page| DiagramFrame
```

### Visual Layout Table (LEFT)

| Frame Layer              | Component                             | Sizer Slot & Props          | Visual Layout & Role                                          |
| :----------------------- | :------------------------------------ | :-------------------------- | :------------------------------------------------------------ |
| **Frame Top**            | `wx.MenuBar`                          | Native Frame Menu           | `File` \| `Edit` \| `Extensions` \| `Help` (spans full width) |
| **Slot 0 (Left Column)** | **`AuiToolBar`** (`self._tb`)         | `prop=0, expand=True`       | `[★ Vertical ToolBar ★]` (`AUI_TB_VERTICAL`) docked on left   |
| **Slot 1 (Right Fill)**  | `UmlNotebook` (`self._umlNotebook`)   | `prop=1, expand=True`       | Right workspace filling remaining window width                |
| ↳ *Left Splitter*        | `UmlProjectTree` (`wx.TreeCtrl`)      | `SplitterWindow` Left Pane  | Project & diagrams hierarchy tree browser                     |
| ↳ *Right Splitter*       | `UmlDiagramManager` (`wx.Simplebook`) | `SplitterWindow` Right Pane | Active `DiagramFrame` (`ShapeCanvas` drawing surface)         |
| **Frame Bottom**         | `wx.StatusBar`                        | Native Frame Status         | Multi-pane status and tool hints (spans full width)           |

---

## 6. Position 4: ToolBar Position = RIGHT

In the **RIGHT** configuration:
* `contentsPane` uses a `horizontal` sizer via `sizedPanel.SetSizerType('horizontal')`.
* `ToolBarCreator` sets the style flag `AUI_TB_VERTICAL`.
* `UmlNotebook` occupies **Sizer Slot 0** (left workspace).
* When `UmlNotebook` is created, `_manuallyDockToolBar()` detaches `self._tb` and appends it at **Sizer Slot 1** (right column edge).

### Hierarchy Diagram (RIGHT Position)

```mermaid
flowchart TD
    classDef tbHighlight fill:#ffe082,stroke:#f57c00,stroke-width:3px,font-weight:bold,color:#000
    classDef panelStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef frameStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef leafStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000

    AppFrame["UmlDiagrammerAppFrame (SizedFrame)"]:::frameStyle
    MenuBar["wx.MenuBar\n(Native Frame Menu)"]:::leafStyle
    StatusBar["wx.StatusBar\n(Native Frame Status)"]:::leafStyle
    ContentsPane["contentsPane: SizedPanel\n(expand=True, proportion=1)\n[Sizer: horizontal]"]:::panelStyle

    AppFrame --> MenuBar
    AppFrame --> ContentsPane
    AppFrame --> StatusBar

    Notebook["SIZER SLOT 0 (LEFT WORKSPACE)\nUmlNotebook (self._umlNotebook)\nprop=1, expand=True"]:::panelStyle
    ToolBar["★ SIZER SLOT 1 (RIGHT DOCKED) ★\nwx.aui.AuiToolBar (self._tb)\nVertical | prop=0, expand=True\nstyle: AUI_TB_DEFAULT_STYLE | AUI_TB_OVERFLOW | AUI_TB_VERTICAL\n(Detached & Re-added via _manuallyDockToolBar)"]:::tbHighlight

    ContentsPane -->|Slot 0: Left Fill| Notebook
    ContentsPane -->|Slot 1: Trailing Right Edge| ToolBar

    ProjectPanel["UmlProjectPanel (wx.SplitterWindow)\n(Per Project Tab)"]:::panelStyle
    Notebook --> ProjectPanel

    ProjectTree["UmlProjectTree (wx.TreeCtrl)\nLeft Pane (Tree Browser)"]:::leafStyle
    DiagramManager["UmlDiagramManager (wx.Simplebook)\nRight Pane (Diagram Switcher)"]:::panelStyle

    ProjectPanel -->|Split Left| ProjectTree
    ProjectPanel -->|Split Right| DiagramManager

    DiagramFrame["Active DiagramFrame (ShapeCanvas)\n(ClassDiagramFrame / UseCase / Sequence)"]:::leafStyle
    DiagramManager -->|Active Page| DiagramFrame
```

### Visual Layout Table (RIGHT)

| Frame Layer               | Component                             | Sizer Slot & Props          | Visual Layout & Role                                                                      |
| :------------------------ | :------------------------------------ | :-------------------------- | :---------------------------------------------------------------------------------------- |
| **Frame Top**             | `wx.MenuBar`                          | Native Frame Menu           | `File` \| `Edit` \| `Extensions` \| `Help` (spans full width)                             |
| **Slot 0 (Left Fill)**    | `UmlNotebook` (`self._umlNotebook`)   | `prop=1, expand=True`       | Left workspace filling remaining window width                                             |
| ↳ *Left Splitter*         | `UmlProjectTree` (`wx.TreeCtrl`)      | `SplitterWindow` Left Pane  | Project & diagrams hierarchy tree browser                                                 |
| ↳ *Right Splitter*        | `UmlDiagramManager` (`wx.Simplebook`) | `SplitterWindow` Right Pane | Active `DiagramFrame` (`ShapeCanvas` drawing surface)                                     |
| **Slot 1 (Right Column)** | **`AuiToolBar`** (`self._tb`)         | `prop=0, expand=True`       | `[★ Vertical ToolBar ★]` (`AUI_TB_VERTICAL`) docked on right (via `_manuallyDockToolBar`) |
| **Frame Bottom**          | `wx.StatusBar`                        | Native Frame Status         | Multi-pane status and tool hints (spans full width)                                       |

---

## 7. AuiToolBar Adjustments & Overflow Handling

To accommodate narrow window dimensions and high-density toolbar items across all 4 docking orientations, `ToolBarCreator` implements several specialized adaptations:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frame as UmlDiagrammerAppFrame
    participant SPanel as SizedPanel (contentsPane)
    participant TBCreator as ToolBarCreator
    participant AuiTB as AuiToolBar (self._tb)
    participant Menu as Overflow wx.Menu

    User->>Frame: Launch or change ToolBarPosition preference
    Frame->>SPanel: SetSizerType('vertical' or 'horizontal')
    Frame->>TBCreator: ToolBarCreator(self, handlers, callback)
    TBCreator->>AuiTB: Create with parent=SPanel, style=(DEFAULT | OVERFLOW [| VERTICAL])
    TBCreator->>AuiTB: SetToolBitmapSize(16x16 .. 64x64)
    TBCreator->>AuiTB: Bind(EVT_AUITOOLBAR_OVERFLOW_CLICK, _onOverflowClick)
    Frame->>AuiTB: Realize()

    alt Trailing Position (BOTTOM or RIGHT)
        Frame->>Frame: _manuallyDockToolBar(SPanel)
        Note over Frame,SPanel: Sizer.Detach(AuiTB) -> Sizer.Add(AuiTB, 0, EXPAND)
    end

    opt Window Resized / Tools Clipped
        User->>AuiTB: Click Overflow Chevron [>>]
        AuiTB->>TBCreator: _onOverflowClick(event)
        TBCreator->>AuiTB: Check GetToolFitsByIndex(i) for all tools
        TBCreator->>Menu: Populate with clipped ToolDefinitions, icons, check states
        TBCreator->>AuiTB: PopupMenu(overflowMenu, calculatedPopupPoint)
        User->>Menu: Select tool
        Menu->>TBCreator: Trigger tool action callback
    end
```

### Key Technical Adaptations
1. **Parentage via `SizedPanel`:**
   Instead of `SetToolBar()` on `wx.Frame`, the `AuiToolBar` is a managed child of `contentsPane`, participating directly in sizer proportion distribution (`prop=0` for toolbar, `prop=1` for `UmlNotebook`).
2. **Overflow Management:**
   Enabling `AUI_TB_OVERFLOW` adds an automatic chevron button when the available window edge cannot fit all tools. `_onOverflowClick` dynamically queries `GetToolFitsByIndex()` to construct a `wx.Menu` that mirrors the hidden tools, their toggle checkmarks, enabled states, and high-resolution icons.
3. **Multi-Resolution Icon Scaling:**
   Toolbar supports icon sizes from Small (16x16), Medium (24x24), Large (32x32), Very Large (48x48), to Extra Large (64x64) via `SetToolBitmapSize()` prior to calling `Realize()`.
4. **Trailing Edge Manual Docking:**
   Because `SizedPanel` manages controls by creation order, `_manuallyDockToolBar()` handles repositioning for `BOTTOM` and `RIGHT` by detaching the toolbar and appending it after the notebook.
