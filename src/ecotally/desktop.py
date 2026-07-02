"""Native Windows desktop interface for EcoTally."""

from __future__ import annotations

import csv
import json
import tempfile
import threading
from pathlib import Path
from tkinter import (
    BOTH,
    END,
    LEFT,
    RIGHT,
    X,
    Y,
    BooleanVar,
    Canvas,
    Frame,
    Label,
    StringVar,
    Tk,
    filedialog,
    messagebox,
    ttk,
)

from . import __version__
from .cli import analyze, render, write_bundle
from .io import _detect_delimiter, read_communities_csv


COLORS = {
    "background": "#EEF3EF",
    "sidebar": "#E7EEE8",
    "surface": "#FFFFFF",
    "surface_alt": "#F3F7F4",
    "surface_selected": "#DDF0E2",
    "line": "#C7D4C9",
    "line_strong": "#8EAA94",
    "muted": "#59685E",
    "text": "#1F2923",
    "green": "#137A3D",
    "green_dark": "#0B5D2C",
    "green_soft": "#E6F1E9",
    "warning": "#A96216",
}


EXAMPLE_DATA = """site,species,abundance
forest-edge,Quercus mongolica,12
forest-edge,Betula platyphylla,8
forest-edge,Lespedeza bicolor,5
forest-core,Quercus mongolica,20
forest-core,Betula platyphylla,4
forest-core,Pinus tabuliformis,3
"""


def preview_tabular_file(path: str | Path, limit: int = 10) -> tuple[list[str], list[list[str]]]:
    """Return headers and a small text preview without interpreting the schema."""

    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=_detect_delimiter(source))
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise ValueError("文件是空的") from exc
        rows = [row for _, row in zip(range(limit), reader)]
    return headers, rows


def analysis_options(
    *,
    sampling: bool,
    uncertainty: bool,
    hill_profile: bool,
    traits_path: str | Path | None,
) -> dict[str, object]:
    """Map student-facing choices to stable analysis parameters."""

    return {
        "bootstrap": 200 if uncertainty else 0,
        "rarefaction": 12 if sampling else 0,
        "hill_orders": [0.0, 0.5, 1.0, 2.0, 3.0] if hill_profile else [],
        "traits_path": Path(traits_path) if traits_path else None,
        "standardize_trait_values": bool(traits_path),
    }


def plain_language_summary(report: dict[str, list[dict[str, object]]]) -> str:
    """Explain the strongest basic result without overstating inference."""

    sites = [row for row in report.get("sites", []) if "shannon" in row]
    if not sites:
        return "没有可计算多样性的非空样方。请先检查数据质量提示。"
    if len(sites) == 1:
        site = sites[0]
        return (
            f"{site['site']} 记录到 {site['richness']} 个物种。"
            "只有一个样方，因此暂时不能比较样方之间的差异。"
        )
    most_even = max(sites, key=lambda row: float(row["pielou_evenness"]))
    richest = max(sites, key=lambda row: int(row["richness"]))
    return (
        f"{richest['site']} 的物种丰富度最高（{richest['richness']} 种）；"
        f"{most_even['site']} 的个体分布最均匀。"
        "这些结果描述当前样本，不等同于因果结论。"
    )


class EcoTallyDesktop:
    """Three-step desktop workflow for students."""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title(f"EcoTally {__version__} · 群落生态分析")
        self.root.geometry("1180x780")
        self.root.minsize(980, 680)
        self.root.configure(bg=COLORS["background"])

        self.source_path: Path | None = None
        self.traits_path: Path | None = None
        self.report: dict[str, list[dict[str, object]]] | None = None
        self.step = 1
        self.analysis_running = False

        self.include_sampling = BooleanVar(value=True)
        self.include_uncertainty = BooleanVar(value=False)
        self.include_hill = BooleanVar(value=True)
        self.include_functional = BooleanVar(value=False)
        self.status_text = StringVar(value="就绪")
        self.file_text = StringVar(value="尚未选择数据文件")
        self.data_summary_text = StringVar(value="")

        self._configure_styles()
        self._build_shell()
        self.show_import()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=28,
            borderwidth=1,
            relief="solid",
            font=("Microsoft YaHei UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["surface_selected"])],
            foreground=[("selected", COLORS["green_dark"])],
        )
        style.configure(
            "Student.TCheckbutton",
            background=COLORS["background"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 12, "bold"),
        )

    def _build_shell(self) -> None:
        self.sidebar = Frame(self.root, bg=COLORS["sidebar"], width=210)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        brand = Frame(self.sidebar, bg=COLORS["sidebar"])
        brand.pack(fill=X, padx=24, pady=(28, 30))
        Label(
            brand,
            text="EcoTally",
            bg=COLORS["sidebar"],
            fg=COLORS["green_dark"],
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        ).pack(fill=X)
        Label(
            brand,
            text="群落分析 · 无代码",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
            anchor="w",
        ).pack(fill=X, pady=(2, 0))

        self.nav_buttons: dict[str, Label] = {}
        for key, text, action in (
            ("start", "开始分析", self.reset),
            ("example", "载入示例数据", self.load_example),
            ("help", "帮助与教程", self.show_help),
            ("about", "关于 EcoTally", self.show_about),
        ):
            label = Label(
                self.sidebar,
                text=text,
                bg=COLORS["sidebar"],
                fg=COLORS["text"],
                font=("Microsoft YaHei UI", 11),
                anchor="w",
                padx=24,
                pady=13,
                cursor="hand2",
            )
            label.pack(fill=X, padx=8, pady=2)
            label.bind("<Button-1>", lambda _event, callback=action: callback())
            self.nav_buttons[key] = label
        self._activate_nav("start")

        status = Frame(self.sidebar, bg=COLORS["sidebar"])
        status.pack(side="bottom", fill=X, padx=24, pady=20)
        Label(
            status,
            textvariable=self.status_text,
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
            anchor="w",
        ).pack(fill=X)

        self.main = Frame(self.root, bg=COLORS["background"])
        self.main.pack(side=RIGHT, fill=BOTH, expand=True)

    def _activate_nav(self, active: str) -> None:
        for key, label in self.nav_buttons.items():
            label.configure(
                bg=COLORS["green_soft"] if key == active else COLORS["sidebar"],
                fg=COLORS["green_dark"] if key == active else COLORS["text"],
            )

    def _clear_main(self) -> None:
        for child in self.main.winfo_children():
            child.destroy()

    def _header(self, title: str, subtitle: str, step: int | None = None) -> Frame:
        header = Frame(self.main, bg=COLORS["background"])
        header.pack(fill=X, padx=58, pady=(34, 12))
        Label(
            header,
            text=title,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 24, "bold"),
            anchor="w",
        ).pack(fill=X)
        Label(
            header,
            text=subtitle,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 11),
            anchor="w",
        ).pack(fill=X, pady=(8, 0))
        if step:
            self._stepper(header, step)
        return header

    def _stepper(self, parent: Frame, active: int) -> None:
        row = Frame(parent, bg=COLORS["background"])
        row.pack(fill=X, pady=(28, 4))
        for index, text in enumerate(("数据", "分析", "结果"), start=1):
            color = COLORS["green"] if index <= active else "#A9B0AB"
            Label(
                row,
                text=f"{index}  {text}",
                bg=COLORS["background"],
                fg=color,
                font=("Microsoft YaHei UI", 10, "bold" if index == active else "normal"),
            ).pack(side=LEFT)
            if index < 3:
                Canvas(
                    row,
                    height=2,
                    width=135,
                    bg=color if index < active else COLORS["line"],
                    highlightthickness=0,
                ).pack(side=LEFT, padx=14)

    def _button(
        self,
        parent: Frame,
        text: str,
        command,
        *,
        primary: bool = False,
        width: int = 16,
    ) -> Label:
        background = COLORS["green"] if primary else COLORS["surface"]
        foreground = "#FFFFFF" if primary else COLORS["green_dark"]
        label = Label(
            parent,
            text=text,
            bg=background,
            fg=foreground,
            font=("Microsoft YaHei UI", 10, "bold"),
            padx=18,
            pady=10,
            width=width,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=COLORS["green"] if not primary else background,
        )
        label.bind("<Button-1>", lambda _event: command())
        return label

    def show_import(self) -> None:
        self.step = 1
        self._clear_main()
        self._activate_nav("start")
        self._header(
            "开始一次群落分析",
            "选择物种丰度表，EcoTally 会帮你计算多样性并生成报告。",
            1,
        )
        content = Frame(self.main, bg=COLORS["background"])
        content.pack(fill=BOTH, expand=True, padx=58, pady=(4, 28))

        Label(
            content,
            text="导入物种丰度表",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 11, "bold"),
            anchor="w",
        ).pack(fill=X, pady=(0, 10))
        drop = Frame(
            content,
            bg=COLORS["surface"],
            height=112,
            highlightbackground="#92AF99",
            highlightthickness=1,
            cursor="hand2",
        )
        drop.pack(fill=X)
        drop.pack_propagate(False)
        drop.bind("<Button-1>", lambda _event: self.choose_file())
        instruction = Label(
            drop,
            text="点击这里选择 CSV、TSV 或分号分隔文件",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 12, "bold"),
            cursor="hand2",
        )
        instruction.pack(pady=(30, 4))
        instruction.bind("<Button-1>", lambda _event: self.choose_file())
        Label(
            drop,
            text="支持长表和宽表；推荐列名 site、species、abundance",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        ).pack()

        self.file_row = Frame(
            content,
            bg=COLORS["surface_alt"],
            highlightbackground=COLORS["line_strong"],
            highlightthickness=1,
        )
        self.file_row.pack(fill=X, pady=(12, 16))
        self.file_label = Label(
            self.file_row,
            textvariable=self.file_text,
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 10),
            anchor="w",
            padx=16,
            pady=10,
        )
        self.file_label.pack(fill=X)

        preview_header = Frame(content, bg=COLORS["background"])
        preview_header.pack(fill=X, pady=(0, 8))
        Label(
            preview_header,
            text="数据预览（前 10 行）",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 11, "bold"),
        ).pack(side=LEFT)
        Label(
            preview_header,
            textvariable=self.data_summary_text,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        ).pack(side=RIGHT)

        # Reserve the action bar before the expandable preview so the primary
        # action remains visible at the minimum supported window height.
        self.import_footer = Frame(content, bg=COLORS["background"])
        self.import_footer.pack(side="bottom", fill=X, pady=(16, 0))
        self.continue_button = self._button(
            self.import_footer,
            "检查数据并继续",
            self.validate_and_continue,
            primary=True,
            width=18,
        )
        self.continue_button.pack(side=RIGHT)

        table_frame = Frame(
            content,
            bg=COLORS["surface"],
            highlightbackground=COLORS["line_strong"],
            highlightthickness=1,
        )
        table_frame.pack(fill=BOTH, expand=True)
        self.preview_table = ttk.Treeview(table_frame, show="headings")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.preview_table.yview)
        self.preview_table.configure(yscrollcommand=scroll.set)
        self.preview_table.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)

    def choose_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="选择群落数据",
            filetypes=[
                ("表格文件", "*.csv *.tsv *.txt"),
                ("所有文件", "*.*"),
            ],
        )
        if filename:
            self.load_file(Path(filename))

    def load_file(self, path: Path) -> None:
        try:
            headers, rows = preview_tabular_file(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("无法读取文件", str(exc))
            return
        self.source_path = path
        self.file_text.set(f"{path.name}  ·  {path.stat().st_size / 1024:.1f} KB  ·  已选择")
        self.file_row.configure(
            bg=COLORS["surface_selected"],
            highlightbackground=COLORS["green"],
            highlightthickness=2,
        )
        self.file_label.configure(
            bg=COLORS["surface_selected"],
            fg=COLORS["green_dark"],
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        self.preview_table.delete(*self.preview_table.get_children())
        self.preview_table["columns"] = headers
        for header in headers:
            self.preview_table.heading(header, text=header)
            self.preview_table.column(header, width=160, minwidth=90, anchor="w")
        self.preview_table.tag_configure("even", background=COLORS["surface"])
        self.preview_table.tag_configure("odd", background=COLORS["surface_alt"])
        for index, row in enumerate(rows):
            padded = row + [""] * (len(headers) - len(row))
            self.preview_table.insert(
                "",
                END,
                values=padded[: len(headers)],
                tags=("even" if index % 2 == 0 else "odd",),
            )
        self.data_summary_text.set(f"{len(headers)} 列 · 已显示 {len(rows)} 行")
        self.status_text.set("数据文件已载入")

    def load_example(self) -> None:
        example = Path(tempfile.gettempdir()) / "ecotally-example.csv"
        example.write_text(EXAMPLE_DATA, encoding="utf-8")
        self.show_import()
        self.load_file(example)

    def validate_and_continue(self) -> None:
        if not self.source_path:
            messagebox.showinfo("请选择文件", "请先选择群落数据文件。")
            return
        try:
            communities = read_communities_csv(self.source_path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("数据需要修改", str(exc))
            return
        species = {
            name
            for community in communities.values()
            for name, abundance in community.items()
            if abundance > 0
        }
        total = sum(sum(community.values()) for community in communities.values())
        self.data_summary_text.set(
            f"{len(communities)} 个样方 · {len(species)} 个物种 · 总丰度 {total:g}"
        )
        self.show_analysis()

    def show_analysis(self) -> None:
        self.step = 2
        self._clear_main()
        self._header(
            "你想了解群落的哪些方面？",
            "保留默认选项就能得到一份完整、容易阅读的报告。",
            2,
        )
        content = Frame(self.main, bg=COLORS["background"])
        content.pack(fill=BOTH, expand=True, padx=58, pady=(4, 28))
        Label(
            content,
            textvariable=self.data_summary_text,
            bg=COLORS["green_soft"],
            fg=COLORS["green_dark"],
            font=("Microsoft YaHei UI", 10, "bold"),
            anchor="w",
            padx=14,
            pady=9,
        ).pack(fill=X, pady=(0, 14))

        options = (
            (
                self.include_sampling,
                "采样够不够",
                "计算覆盖率、Chao1 和稀释曲线，判断是否可能漏掉较多物种。",
            ),
            (
                self.include_uncertainty,
                "结果有多稳定",
                "用可复现的 Bootstrap 给核心指标加上区间。",
            ),
            (
                self.include_hill,
                "稀有种和优势种的影响",
                "生成 Hill 多样性谱，观察不同权重下的群落变化。",
            ),
            (
                self.include_functional,
                "物种性状有什么差异",
                "选择额外性状表后，计算功能离散度和 Rao’s Q。",
            ),
        )
        for variable, title, description in options:
            row = Frame(content, bg=COLORS["background"])
            row.pack(fill=X, pady=3)
            ttk.Checkbutton(
                row,
                text=title,
                variable=variable,
                style="Student.TCheckbutton",
            ).pack(anchor="w")
            Label(
                row,
                text=description,
                bg=COLORS["background"],
                fg=COLORS["muted"],
                font=("Microsoft YaHei UI", 9),
                anchor="w",
            ).pack(fill=X, padx=(28, 0), pady=(2, 8))

        trait_row = Frame(content, bg=COLORS["surface_alt"])
        trait_row.pack(fill=X, pady=(10, 0))
        self.trait_text = StringVar(value="可选：尚未选择物种性状表")
        Label(
            trait_row,
            textvariable=self.trait_text,
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
            anchor="w",
            padx=14,
            pady=10,
        ).pack(side=LEFT, fill=X, expand=True)
        self._button(
            trait_row,
            "选择性状表",
            self.choose_traits,
            width=12,
        ).pack(side=RIGHT, padx=8, pady=7)

        footer = Frame(content, bg=COLORS["background"])
        footer.pack(side="bottom", fill=X)
        self._button(footer, "返回", self.show_import, width=10).pack(side=LEFT)
        self.start_button = self._button(
            footer, "开始分析", self.start_analysis, primary=True, width=16
        )
        self.start_button.pack(side=RIGHT)

    def choose_traits(self) -> None:
        filename = filedialog.askopenfilename(
            title="选择物种性状表",
            filetypes=[("表格文件", "*.csv *.tsv *.txt"), ("所有文件", "*.*")],
        )
        if filename:
            self.traits_path = Path(filename)
            self.trait_text.set(f"性状表：{self.traits_path.name}")
            self.include_functional.set(True)

    def start_analysis(self) -> None:
        if self.analysis_running:
            return
        if not self.source_path:
            self.show_import()
            return
        if self.include_functional.get() and not self.traits_path:
            messagebox.showinfo("需要性状表", "请先选择物种性状表，或取消性状分析。")
            return
        self.analysis_running = True
        self.status_text.set("正在分析…")
        self.root.configure(cursor="watch")
        self.start_button.configure(
            text="正在分析，请稍候…",
            bg=COLORS["green_dark"],
            cursor="watch",
        )
        self.root.update_idletasks()
        options = analysis_options(
            sampling=self.include_sampling.get(),
            uncertainty=self.include_uncertainty.get(),
            hill_profile=self.include_hill.get(),
            traits_path=self.traits_path if self.include_functional.get() else None,
        )

        def worker() -> None:
            try:
                report = analyze(self.source_path, **options)
            except (OSError, ValueError) as exc:
                self.root.after(0, lambda: self._analysis_failed(str(exc)))
                return
            self.root.after(0, lambda: self._analysis_complete(report))

        threading.Thread(target=worker, daemon=True).start()

    def _analysis_failed(self, message: str) -> None:
        self.analysis_running = False
        self.root.configure(cursor="")
        self.status_text.set("分析失败")
        if self.start_button.winfo_exists():
            self.start_button.configure(
                text="重新开始分析",
                bg=COLORS["green"],
                cursor="hand2",
            )
        messagebox.showerror("分析未完成", message)

    def _analysis_complete(self, report: dict[str, list[dict[str, object]]]) -> None:
        self.analysis_running = False
        self.root.configure(cursor="")
        self.report = report
        self.status_text.set("分析完成")
        self.show_results()

    def show_results(self) -> None:
        self.step = 3
        self._clear_main()
        self._header(
            "分析完成",
            plain_language_summary(self.report or {}),
            3,
        )
        content = Frame(self.main, bg=COLORS["background"])
        content.pack(fill=BOTH, expand=True, padx=58, pady=(4, 28))

        report = self.report or {}
        dataset = (report.get("dataset") or [{}])[0]
        quality = report.get("quality") or []
        summary = Frame(content, bg=COLORS["surface_alt"])
        summary.pack(fill=X, pady=(0, 16))
        for label, value in (
            ("样方", dataset.get("site_count", 0)),
            ("物种", dataset.get("gamma_richness", 0)),
            ("总丰度", f"{float(dataset.get('total_abundance', 0)):g}"),
            ("数据质量", "需留意" if quality else "良好"),
        ):
            cell = Frame(summary, bg=COLORS["surface_alt"])
            cell.pack(side=LEFT, expand=True, fill=X, padx=18, pady=12)
            Label(
                cell,
                text=str(value),
                bg=COLORS["surface_alt"],
                fg=COLORS["green_dark"],
                font=("Segoe UI", 18, "bold"),
            ).pack()
            Label(
                cell,
                text=label,
                bg=COLORS["surface_alt"],
                fg=COLORS["muted"],
                font=("Microsoft YaHei UI", 9),
            ).pack()

        columns = (
            "site",
            "richness",
            "shannon",
            "simpson",
            "pielou_evenness",
        )
        self.result_footer = Frame(content, bg=COLORS["background"])
        self.result_footer.pack(side="bottom", fill=X, pady=(16, 0))
        self._button(
            self.result_footer, "返回调整", self.show_analysis, width=11
        ).pack(side=LEFT)
        self._button(
            self.result_footer,
            "导出 JSON",
            lambda: self.export_file("json"),
            width=11,
        ).pack(side=RIGHT, padx=(8, 0))
        self.export_bundle_button = self._button(
            self.result_footer,
            "导出完整报告",
            self.export_bundle,
            primary=True,
            width=15,
        )
        self.export_bundle_button.pack(side=RIGHT)

        quality_text = (
            "数据质量检查未发现明显问题。"
            if not quality
            else f"发现 {len(quality)} 条数据质量提示；完整报告中有详细说明。"
        )
        Label(
            content,
            text=quality_text,
            bg=COLORS["background"],
            fg=COLORS["warning"] if quality else COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
            anchor="w",
        ).pack(side="bottom", fill=X, pady=(10, 0))

        table_frame = Frame(
            content,
            bg=COLORS["surface"],
            highlightbackground=COLORS["line_strong"],
            highlightthickness=1,
        )
        table_frame.pack(fill=BOTH, expand=True)
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        labels = {
            "site": "样方",
            "richness": "丰富度",
            "shannon": "Shannon",
            "simpson": "Simpson",
            "pielou_evenness": "均匀度",
        }
        for column in columns:
            table.heading(column, text=labels[column])
            table.column(column, anchor="w", width=150)
        table.tag_configure("even", background=COLORS["surface"])
        table.tag_configure("odd", background=COLORS["surface_alt"])
        for index, row in enumerate(report.get("sites", [])):
            table.insert(
                "",
                END,
                values=[
                    row.get("site", ""),
                    row.get("richness", "—"),
                    self._number(row.get("shannon")),
                    self._number(row.get("simpson")),
                    self._number(row.get("pielou_evenness")),
                ],
                tags=("even" if index % 2 == 0 else "odd",),
            )
        table.pack(fill=BOTH, expand=True)

    @staticmethod
    def _number(value: object) -> str:
        return "—" if value is None else f"{float(value):.4f}"

    def export_file(self, output_format: str) -> None:
        if not self.report:
            return
        extension = {"json": ".json", "markdown": ".md", "svg": ".svg"}[output_format]
        filename = filedialog.asksaveasfilename(
            title="保存分析结果",
            defaultextension=extension,
            filetypes=[(output_format.upper(), f"*{extension}")],
        )
        if not filename:
            return
        Path(filename).write_text(
            render(self.report, output_format), encoding="utf-8"
        )
        self.status_text.set(f"已保存 {Path(filename).name}")
        messagebox.showinfo("导出完成", f"结果已保存到：\n{filename}")

    def export_bundle(self) -> None:
        if not self.report:
            return
        directory = filedialog.askdirectory(title="选择完整报告保存文件夹")
        if not directory:
            return
        output = Path(directory) / "EcoTally-analysis"
        files = write_bundle(self.report, output)
        markdown = render(self.report, "markdown")
        (output / "report.md").write_text(markdown, encoding="utf-8")
        self.status_text.set("完整报告已导出")
        messagebox.showinfo(
            "导出完成",
            f"已生成 {len(files) + 1} 个文件：\n{output}",
        )

    def show_help(self) -> None:
        self._clear_main()
        self._activate_nav("help")
        self._header("帮助与教程", "三步完成一次可复现的群落分析。")
        text = (
            "1. 准备数据\n"
            "长表至少包含 site、species、abundance 三列；也支持每列一个物种的宽表。\n\n"
            "2. 选择问题\n"
            "默认选项适合课程作业和初步探索。性状分析需要额外的物种性状表。\n\n"
            "3. 阅读结果\n"
            "先看数据质量，再比较丰富度、Shannon 和均匀度。不要把描述性差异直接当作因果结论。\n\n"
            "遇到问题时，可先用左侧“载入示例数据”检查软件是否正常。"
        )
        Label(
            self.main,
            text=text,
            justify=LEFT,
            wraplength=760,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 11),
            anchor="nw",
        ).pack(fill=BOTH, expand=True, padx=58, pady=20)

    def show_about(self) -> None:
        self._clear_main()
        self._activate_nav("about")
        self._header("关于 EcoTally", "透明、轻量、为学习群落生态学而做。")
        Label(
            self.main,
            text=(
                f"EcoTally {__version__}\n\n"
                "它把物种丰度表转换成容易阅读的多样性报告，"
                "计算过程可追溯，并记录输入文件哈希与分析参数。\n\n"
                "开源许可证：MIT\n"
                "项目主页：https://github.com/B2N06/ecotally-tool--"
            ),
            justify=LEFT,
            wraplength=760,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Microsoft YaHei UI", 11),
            anchor="nw",
        ).pack(fill=BOTH, expand=True, padx=58, pady=20)

    def reset(self) -> None:
        self.source_path = None
        self.traits_path = None
        self.report = None
        self.file_text.set("尚未选择数据文件")
        self.data_summary_text.set("")
        self.status_text.set("就绪")
        self.show_import()


def main() -> None:
    root = Tk()
    EcoTallyDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
