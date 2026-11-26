# Panduan Project dan Presentasi

## Apa yang diprediksi?

Sistem memprediksi **kuat tekan beton dalam MPa** berdasarkan tujuh komponen campuran per meter kubik dan umur beton saat diuji. Contoh keluaran 35 MPa berarti model memperkirakan beton mampu menerima tekanan sekitar 35 megapascal sebelum mengalami kegagalan pada pengujian tekan.

## Mengapa penting?

Kuat tekan merupakan salah satu indikator utama kemampuan beton menahan beban tekan. Prediksi awal membantu peneliti atau perencana membandingkan alternatif komposisi sebelum melakukan pengujian laboratorium yang tetap wajib dilakukan untuk validasi nyata.

## Alur program

1. Membaca dataset resmi UCI.
2. Memeriksa kolom, nilai kosong, nilai tidak logis, dan duplikat.
3. Membagi data menjadi 70% train, 15% validation, dan 15% test.
4. Melatih Multiple Linear Regression dan Random Forest Regression pada train.
5. Membandingkan MAE, RMSE, dan R² pada validation.
6. Memilih model dengan RMSE validation terendah.
7. Melatih ulang kedua model dengan gabungan train dan validation.
8. Menguji performa akhir pada test yang belum digunakan sebelumnya.
9. Menyimpan model terbaik dan menggunakannya pada aplikasi Streamlit.

## Rumus yang bisa ditulis di papan

### Multiple Linear Regression

$$\hat{y}=\beta_0+\beta_1x_1+\beta_2x_2+\cdots+\beta_8x_8$$

`x₁` sampai `x₈` adalah delapan input, `β₀` adalah konstanta, `β₁` sampai `β₈` adalah koefisien yang dipelajari, dan `ŷ` adalah prediksi kuat tekan.

### Random Forest Regression

$$\hat{y}=\frac{1}{T}\sum_{t=1}^{T}f_t(x)$$

Setiap decision tree menghasilkan prediksi. Random Forest mengambil rata-rata prediksi dari seluruh tree sehingga hasil lebih stabil.

### MAE

$$MAE=\frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|$$

Jika nilai aktual 40 MPa dan prediksi 36 MPa, galat absolutnya adalah `|40 − 36| = 4 MPa`.

### RMSE

$$RMSE=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}$$

RMSE lebih sensitif terhadap kesalahan besar karena selisih dikuadratkan.

### R²

$$R^2=1-\frac{\sum(y_i-\hat{y}_i)^2}{\sum(y_i-\bar{y})^2}$$

Nilai mendekati 1 menunjukkan model menjelaskan variasi target dengan lebih baik.

## Hasil project ini

| Model | Split | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Multiple Linear Regression | Validation | 8,13 MPa | 10,30 MPa | 0,580 |
| Random Forest Regression | Validation | 3,26 MPa | 4,75 MPa | 0,911 |
| Multiple Linear Regression | Test | 8,81 MPa | 11,01 MPa | 0,558 |
| Random Forest Regression | Test | 3,39 MPa | 4,73 MPa | 0,918 |

Random Forest dipilih karena memiliki RMSE validation paling rendah. Nilai test hanya dipakai untuk menilai performa akhir, bukan untuk memilih model.

## Batasan yang perlu disampaikan

- Prediksi hanya berlaku dalam rentang atribut yang ada pada dataset.
- Dataset tidak memuat metode curing, kondisi lingkungan, atau sumber material lokal Indonesia.
- Hasil bukan penetapan mutu beton dan tidak menggantikan uji laboratorium.
- Model cocok disebut alat estimasi awal atau media penelitian pembelajaran.

## Urutan demo saat presentasi

1. Tunjukkan delapan input dan target MPa.
2. Jelaskan pembagian train, validation, dan test.
3. Tampilkan tabel perbandingan metrik.
4. Jelaskan mengapa Random Forest dipilih.
5. Masukkan satu contoh komposisi di aplikasi.
6. Tekankan bahwa keluaran adalah estimasi awal.
