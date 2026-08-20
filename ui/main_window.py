from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from calc.formulas import calculate_all
from data.materials import MATERIALS
from ui.report import generate_html_report


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Schnittdatenrechner — Fräsen")
        self.setMinimumWidth(800)
        self._report_data: dict = {}
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI aufbauen
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # Projektname
        proj_row = QHBoxLayout()
        lbl = QLabel("<b>Projektname:</b>")
        lbl.setFixedWidth(100)
        proj_row.addWidget(lbl)
        self.le_project = QLineEdit()
        self.le_project.setPlaceholderText("z. B. Gehäuse AlMg3 — Charge 01")
        self.le_project.setFixedHeight(30)
        proj_row.addWidget(self.le_project)
        root.addLayout(proj_row)

        # Eingaben / Ergebnisse nebeneinander
        content_row = QHBoxLayout()
        content_row.addWidget(self._build_input_group(), stretch=55)
        content_row.addWidget(self._build_results_group(), stretch=45)
        root.addLayout(content_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_calc = QPushButton("⚙  Berechnen")
        btn_calc.setFixedHeight(38)
        btn_calc.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        btn_calc.clicked.connect(self._calculate)

        self.btn_print = QPushButton("🖨  Report drucken …")
        self.btn_print.setFixedHeight(38)
        self.btn_print.setEnabled(False)
        self.btn_print.clicked.connect(self._print_report)

        btn_row.addWidget(btn_calc)
        btn_row.addWidget(self.btn_print)
        root.addLayout(btn_row)

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Eingaben")
        form = QFormLayout(group)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setSpacing(6)

        # Werkstoff
        self.cb_material = QComboBox()
        self.cb_material.addItems(list(MATERIALS.keys()))
        self.cb_material.currentIndexChanged.connect(self._on_material_changed)
        form.addRow("Werkstoff:", self.cb_material)

        self._add_separator(form)

        # Werkzeug
        self.sb_D  = self._dspin(0.1, 500.0,  10.0, 1, " mm")
        self.sb_z  = self._ispin(1, 30, 4)
        self.sb_re = self._dspin(0.0,  10.0,   0.8, 2, " mm")
        form.addRow("Durchmesser D:", self.sb_D)
        form.addRow("Schneidenzahl z:", self.sb_z)
        form.addRow("Eckenradius rε:", self.sb_re)

        self._add_separator(form)

        # Schnittparameter
        self.sb_vc = self._dspin(1.0, 3000.0, 150.0, 0, " m/min")
        self.sb_fz = self._dspin(0.001, 5.0,   0.10, 3, " mm/z")
        self.sb_ap = self._dspin(0.01, 500.0,   3.0, 2, " mm")
        self.sb_ae = self._dspin(0.01, 500.0,   5.0, 2, " mm")
        form.addRow("Schnittgeschw. vc:", self.sb_vc)
        form.addRow("Zahnvorschub fz:",   self.sb_fz)
        form.addRow("Schnitttiefe ap:",   self.sb_ap)
        form.addRow("Schnittbreite ae:",  self.sb_ae)

        self._add_separator(form)

        # Maschine
        self.sb_eta   = self._dspin(0.5,    1.0,  0.80, 2, "")
        self.sb_n_max = self._dspin(0.0, 100000.0, 12000.0, 0, " U/min")
        self.sb_n_max.setSpecialValueText("— kein Limit")
        self.sb_P_max = self._dspin(0.0,  500.0,   7.5, 1, " kW")
        self.sb_P_max.setSpecialValueText("— kein Limit")
        form.addRow("Wirkungsgrad η:",    self.sb_eta)
        form.addRow("Max. Drehzahl:",     self.sb_n_max)
        form.addRow("Spindelleistung:",   self.sb_P_max)

        self._add_separator(form)

        # Richtwert-Hinweis
        self.lbl_hint = QLabel()
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setStyleSheet("color: #555; font-size: 9px;")
        form.addRow("Richtwert:", self.lbl_hint)

        self._on_material_changed(0)
        return group

    def _build_results_group(self) -> QGroupBox:
        group = QGroupBox("Ergebnisse")
        form = QFormLayout(group)
        form.setSpacing(6)

        bold_font = QFont("Arial", 11, QFont.Weight.Bold)

        def _rlabel() -> QLabel:
            lbl = QLabel("—")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl.setFont(bold_font)
            lbl.setStyleSheet("color: #1a3c5e;")
            return lbl

        self.lbl_n   = _rlabel(); form.addRow("Drehzahl n:",          self.lbl_n)
        self.lbl_vf  = _rlabel(); form.addRow("Tischvorschub vf:",     self.lbl_vf)
        self.lbl_Q   = _rlabel(); form.addRow("Zeitspanvolumen Q:",    self.lbl_Q)
        self.lbl_Fc  = _rlabel(); form.addRow("Schnittkraft Fc:",       self.lbl_Fc)
        self.lbl_Pc  = _rlabel(); form.addRow("Schnittleistung Pc:",   self.lbl_Pc)
        self.lbl_Pa  = _rlabel(); form.addRow("Antriebsleistung Pa:",  self.lbl_Pa)
        self.lbl_M   = _rlabel(); form.addRow("Drehmoment M:",         self.lbl_M)
        self.lbl_hex = _rlabel(); form.addRow("Spanungsdicke hex:",    self.lbl_hex)
        self.lbl_Rz  = _rlabel(); form.addRow("Rauheit Rz (theor.):", self.lbl_Rz)

        self.lbl_warn = QLabel()
        self.lbl_warn.setWordWrap(True)
        self.lbl_warn.setStyleSheet("color: #c00; font-size: 9px;")
        form.addRow(self.lbl_warn)

        return group

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_material_changed(self, _index: int) -> None:
        mat = MATERIALS[self.cb_material.currentText()]
        self.sb_vc.setValue(mat["vc_default"])
        self.sb_fz.setValue(mat["fz_default"])
        self.lbl_hint.setText(
            f"vc: {mat['vc_min']}–{mat['vc_max']} m/min  "
            f"|  fz: {mat['fz_min']}–{mat['fz_max']} mm/z  "
            f"|  kc1.1 = {mat['kc11']} N/mm²  "
            f"|  mc = {mat['mc']}"
        )

    def _calculate(self) -> None:
        mat_name = self.cb_material.currentText()
        mat = MATERIALS[mat_name]

        vc  = self.sb_vc.value()
        D   = self.sb_D.value()
        z   = self.sb_z.value()
        fz  = self.sb_fz.value()
        ap  = self.sb_ap.value()
        ae  = self.sb_ae.value()
        re  = self.sb_re.value()
        eta = self.sb_eta.value()
        n_max = self.sb_n_max.value() or None
        P_max = self.sb_P_max.value() or None

        try:
            r = calculate_all(vc, D, z, fz, ap, ae, re, mat["kc11"], mat["mc"], eta, n_max, P_max)
        except Exception as exc:
            QMessageBox.critical(self, "Berechnungsfehler", str(exc))
            return

        self.lbl_n.setText(f"{r['n']:,.0f} U/min")
        self.lbl_vf.setText(f"{r['vf']:,.1f} mm/min")
        self.lbl_Q.setText(f"{r['Q']:.2f} cm³/min")
        self.lbl_Fc.setText(f"{r['Fc']:.1f} N")
        self.lbl_Pc.setText(f"{r['Pc']:.2f} kW")
        self.lbl_Pa.setText(f"{r['Pa']:.2f} kW")
        self.lbl_M.setText(f"{r['M']:.2f} Nm")
        self.lbl_hex.setText(f"{r['hex']:.3f} mm")
        self.lbl_Rz.setText(f"{r['Rz']:.1f} µm")

        self.lbl_warn.setText("⚠  " + "\n⚠  ".join(r["warnings"]) if r["warnings"] else "")

        self._report_data = {
            "project": self.le_project.text().strip() or "Ohne Projektname",
            "date": date.today().strftime("%d.%m.%Y"),
            "material": mat_name,
            "inputs": {
                "D": D, "z": z, "re": re,
                "vc": vc, "fz": fz, "ap": ap, "ae": ae,
                "eta": eta,
                "n_max": n_max,
                "P_max": P_max,
            },
            "results": r,
            "warnings": r["warnings"],
        }
        self.btn_print.setEnabled(True)

    def _print_report(self) -> None:
        if not self._report_data:
            return
        html = generate_html_report(self._report_data)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle("Druckvorschau — Schnittdaten-Report")
        preview.paintRequested.connect(lambda p: _render_html_to_printer(html, p))
        preview.exec()

    # ------------------------------------------------------------------
    # Hilfsmethoden
    # ------------------------------------------------------------------

    @staticmethod
    def _dspin(
        min_v: float, max_v: float, default: float, decimals: int, suffix: str
    ) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(min_v, max_v)
        sb.setDecimals(decimals)
        sb.setValue(default)
        if suffix:
            sb.setSuffix(suffix)
        return sb

    @staticmethod
    def _ispin(min_v: int, max_v: int, default: int) -> QSpinBox:
        sb = QSpinBox()
        sb.setRange(min_v, max_v)
        sb.setValue(default)
        return sb

    @staticmethod
    def _add_separator(form: QFormLayout) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ccc;")
        form.addRow(line)


def _render_html_to_printer(html: str, printer: QPrinter) -> None:
    doc = QTextDocument()
    doc.setHtml(html)
    doc.print(printer)
