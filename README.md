# IF3170 G38 — AI is Love

Tugas Besar 1 IF3170 Inteligensi Artifisial, 2026/2027.

## Persyaratan

- Python 3.10 atau lebih baru
- Matplotlib untuk grafik riwayat CLI
- Plotly untuk visualisasi 3D interaktif

Pasang dependensi menggunakan interpreter Python yang akan dipakai menjalankan program:

```powershell
python -m pip install matplotlib plotly
```

Jalankan semua perintah berikut dari direktori utama repositori.

## Mode terminal

Contoh menjalankan Hill Climbing:

```powershell
python src/main.py --algorithm hc --testcase testcase_1.json
```

Pilihan `--algorithm`:

| Nilai | Algoritma |
| --- | --- |
| `hc` | Hill Climbing |
| `sa` | Simulated Annealing |
| `ga` | Genetic Algorithm v1 |
| `ga2` | Genetic Algorithm v2 |

Contoh menjalankan algoritma lain:

```powershell
python src/main.py --algorithm sa --testcase testcase_1.json --iterations 500
python src/main.py --algorithm ga --testcase testcase_1.json --population 50 --iterations 100
python src/main.py --algorithm ga2 --testcase testcase_1.json --population 50 --iterations 100
```

Argumen yang tersedia:

| Argumen | Kegunaan |
| --- | --- |
| `--testcase` | Nama file JSON di `data/`; pilihan yang tersedia ditampilkan oleh `--help`. |
| `--algorithm` | Memilih `hc`, `sa`, `ga`, atau `ga2`. |
| `--hc-mode` | Varian HC: `steepest`, `stochastic`, `sideway`, atau `random-restart`. Hanya berlaku untuk `hc`. |
| `--iterations` | Batas iterasi HC/SA atau jumlah generasi GA. |
| `--restarts` | Batas restart untuk HC dengan mode `random-restart`. |
| `--population` | Ukuran populasi untuk `ga` dan `ga2`. |
| `--no-plot` | Tidak menyimpan grafik riwayat PNG. Visualisasi 3D tetap dibuat jika state akhir valid. |

Nilai default dan contoh tambahan bisa dilihat dengan:

```powershell
python src/main.py --help
```

CLI mencetak ringkasan hasil. Grafik riwayat PNG dan visualisasi 3D HTML disimpan ke `results/`. HTML menampilkan state awal atau akhir melalui dropdown, beserta ringkasan dan rincian paket. Buka file HTML di browser untuk memutar tampilan 3D.
