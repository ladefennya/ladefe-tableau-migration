"""Pruebas del piloto de abandono: invariantes del payload y paridad del redondeo JS/Python.

python -m unittest discover -s prototypes/pilot-abandono -p 'test_*.py' -v
"""
import json
import re
import shutil
import subprocess
import unittest
from collections import Counter
from pathlib import Path

from prepare_pilot import round1

HERE = Path(__file__).parent
PAYLOAD = json.loads((HERE / "pilot_data.json").read_text(encoding="utf-8"))


class PayloadTests(unittest.TestCase):
    def test_24_provincias_y_13_ciclos(self):
        self.assertEqual(len(PAYLOAD["provinces"]), 24)
        self.assertEqual(len(PAYLOAD["periods"]), 13)
        self.assertEqual(PAYLOAD["periods"][-1], "2024-2025")

    def test_sin_claves_duplicadas(self):
        keys = Counter((r[0], r[1], r[2], r[3], r[4]) for r in PAYLOAD["observations"])
        self.assertEqual(max(keys.values()), 1)

    def test_cada_provincia_tiene_total_por_nivel_y_ciclo(self):
        have = {(r[0], r[3], r[4]) for r in PAYLOAD["observations"] if r[1] == "total"}
        for level in ("primary", "secondary"):
            for geo in PAYLOAD["provinces"] + ["00"]:
                for period in PAYLOAD["periods"]:
                    self.assertIn((level, geo, period), have)

    def test_verificacion_contra_tableau_por_vista(self):
        # 85 comparaciones: el total nacional 2024-2025 está en dos vistas (D.5 coincide; D.1/D.3 bloqueada).
        self.assertEqual(PAYLOAD["summary"]["tableauComparisons"], 85)
        self.assertEqual(PAYLOAD["summary"]["statusCounts"], {
            "matched_at_one_decimal": 69, "compatible_with_double_rounding": 1, "blocked_temporal_label_conflict": 15})

    def test_negativos_se_conservan(self):
        self.assertGreater(sum(r[5] < 0 for r in PAYLOAD["observations"]), 0)

    def test_subdivisiones_no_estan_en_el_mapa(self):
        codes = {f["properties"]["in1"] for f in PAYLOAD["geometry"]["features"]}
        self.assertNotIn("06-CON", codes)
        self.assertEqual(codes, set(PAYLOAD["provinces"]))

    def test_geometria_validada_con_malvinas(self):
        g = PAYLOAD["geometryCheck"]
        self.assertEqual((g["invalid"], g["overlaps"]), (0, 0))
        self.assertGreater(g["malvinasKm2"], 10_000)


class BicontinentalTests(unittest.TestCase):
    def test_recuadro_antartico_presente_y_validado(self):
        inset = PAYLOAD["inset"]["features"]
        self.assertEqual(len(inset), 1)
        self.assertEqual(inset[0]["properties"]["in1"], "94")
        parts = PAYLOAD["geometryCheck"]["insetParts"]
        for name in ("Península Antártica", "Islas Orcadas del Sur", "Islas Georgias del Sur", "Islas Sandwich del Sur"):
            self.assertGreater(parts[name], 0, name)

    def test_plantilla_dibuja_recuadro_y_malvinas(self):
        html = (HERE / "pilot_template.html").read_text(encoding="utf-8")
        self.assertIn("insetSVG(", html)
        self.assertIn("Islas Malvinas", html)
        self.assertIn("Antártida Argentina", html)


class EmbeddingTests(unittest.TestCase):
    def test_url_compartible_no_rompe_en_vista_previa_aislada(self):
        html = (HERE / "pilot_template.html").read_text(encoding="utf-8")
        start = html.index("function writeURL()")
        body = html[start:html.index("\n}", start)]
        self.assertIn("try {", body)
        self.assertIn("location.protocol === 'about:'", body)


class RoundingTests(unittest.TestCase):
    def test_half_up_decimal(self):
        self.assertEqual(round1(8.0471945354), 8.0)  # el caso del doble redondeo: el valor exacto da 8,0
        self.assertEqual(round1(0.15), 0.2)  # 0.15 en binario es 0.1499…; HALF_UP decimal da 0,2
        self.assertEqual(round1(-0.0500745554), -0.1)
        self.assertEqual(round1(2.25), 2.3)

    @unittest.skipUnless(shutil.which("node"), "node no disponible")
    def test_paridad_js_python_en_todos_los_valores(self):
        html = (HERE / "pilot_template.html").read_text(encoding="utf-8")
        fn = re.search(r"function round1\(v\) \{.*?\n\}", html, re.S).group(0)
        values = [r[5] for r in PAYLOAD["observations"]] + [0.15, 2.25, -0.05, 1e-7]
        script = fn + "\nconst vals=" + json.dumps(values) + ";console.log(JSON.stringify(vals.map(round1)));"
        out = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
        expected = [round1(v) for v in values]
        mismatches = [(v, a, b) for v, a, b in zip(values, out, expected) if a != b]
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
