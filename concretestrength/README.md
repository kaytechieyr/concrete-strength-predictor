# Concrete Strength Predictor

Implementasi project:

> **Sistem Prediksi Kuat Tekan Beton Berdasarkan Komposisi Campuran dan Umur Menggunakan Multiple Linear Regression dan Random Forest Regression**

Sistem membandingkan dua metode regresi dan menyajikan model terbaik melalui form Streamlit. Target yang diprediksi adalah kuat tekan beton dalam MPa.

## Dataset

Dataset berasal dari [UCI Machine Learning Repository](https://doi.org/10.24432/C5PK67) dan berlisensi CC BY 4.0. Dataset asli memiliki 1.030 baris, delapan fitur numerik, satu target, dan tidak memiliki nilai kosong. Pipeline menghapus 25 duplikat identik sehingga 1.005 baris digunakan.

Delapan fitur terdiri dari semen, blast furnace slag, fly ash, air, superplasticizer, agregat kasar, agregat halus, dan umur beton.

## Hasil Utama

| Model | Split | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Multiple Linear Regression | Validation | 8,13 MPa | 10,30 MPa | 0,580 |
| Random Forest Regression | Validation | 3,26 MPa | 4,75 MPa | 0,911 |
| Multiple Linear Regression | Test | 8,81 MPa | 11,01 MPa | 0,558 |
| Random Forest Regression | Test | 3,39 MPa | 4,73 MPa | 0,918 |

Random Forest Regression dipilih berdasarkan RMSE validation terendah. Data test tidak digunakan dalam pemilihan model.

## Struktur Folder

```text
concrete-strength-predictor/
├── app.py
├── train.py
├── requirements.txt
├── data/
│   ├── README.md
│   └── raw/concrete_compressive_strength.csv
├── models/
│   ├── best_model.joblib
│   └── model_metadata.json
├── notebooks/ConcreteStrength_Colab.ipynb
├── results/
│   ├── model_comparison.csv
│   ├── model_comparison.png
│   ├── actual_vs_predicted.csv
│   ├── actual_vs_predicted.png
│   └── feature_importance.csv
├── tests/test_train.py
└── docs/
    ├── PANDUAN_GITHUB.md
    └── PANDUAN_PROYEK_DAN_PRESENTASI.md
```

## Cara Menjalankan di Windows

Pastikan Python dan Git telah terpasang. Buka terminal di folder project, lalu jalankan:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python train.py
streamlit run app.py
```

Browser akan membuka aplikasi. Jika tidak terbuka otomatis, akses alamat lokal yang tampil pada terminal, biasanya `http://localhost:8501`.

## Menjalankan Pengujian

```powershell
python -m unittest discover -s tests -v
```

## Menjalankan di Google Colab

1. Buka https://colab.research.google.com.
2. Pilih **Upload**.
3. Unggah `notebooks/ConcreteStrength_Colab.ipynb`.
4. Pilih **Runtime > Run all**.

Notebook mengambil dataset resmi UCI secara langsung sehingga file CSV tidak perlu diunggah manual.

## Dokumen Pendukung

- [Penjelasan project dan bahan presentasi](docs/PANDUAN_PROYEK_DAN_PRESENTASI.md)
- [Panduan upload ke GitHub](docs/PANDUAN_GITHUB.md)
- [Keterangan dataset](data/README.md)

## Batasan

Model menghasilkan estimasi awal kuat tekan beton berdasarkan delapan variabel pada dataset eksperimen UCI. Penggunaan model dibatasi pada rentang nilai yang terdapat dalam dataset. Faktor di luar dataset, seperti karakteristik bahan dan proses perawatan beton, belum diperhitungkan. Hasil prediksi tidak dapat digunakan sebagai penetapan mutu beton tanpa pengujian tekan di laboratorium.

## Sitasi Dataset

Yeh, I. C. (1998). *Concrete Compressive Strength* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5PK67
