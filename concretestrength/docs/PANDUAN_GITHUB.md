# Panduan Mengunggah Project ke GitHub

## 1. Buat repository

1. Masuk ke https://github.com/new.
2. Isi nama repository: `concrete-strength-predictor`.
3. Pilih **Public** jika dosen harus dapat membukanya tanpa izin, atau **Private** jika hanya ingin dibagikan kepada anggota tertentu.
4. Jangan centang README, `.gitignore`, atau license karena ketiganya sudah/akan tersedia dari folder project.
5. Klik **Create repository**.

## 2. Buka terminal pada folder project

Di Windows, ekstrak ZIP lalu buka folder `concrete-strength-predictor`. Klik kanan area kosong dan pilih **Open in Terminal**, atau jalankan:

```powershell
cd "LOKASI_FOLDER\concrete-strength-predictor"
```

## 3. Atur identitas Git satu kali

Ganti email dengan email akun GitHub milikmu.

```powershell
git config --global user.name "Bunga Makayla Nasywanaya"
git config --global user.email "EMAIL_GITHUB_KAMU"
```

## 4. Unggah project pertama kali

Ganti `USERNAME` dengan username GitHub milikmu.

```powershell
git init -b main
git add .
git commit -m "Initial concrete strength prediction project"
git remote add origin https://github.com/USERNAME/concrete-strength-predictor.git
git push -u origin main
```

Jika GitHub meminta autentikasi, lanjutkan melalui browser. Setelah selesai, refresh halaman repository.

## 5. Mengunggah perubahan berikutnya

```powershell
git add .
git commit -m "Update concrete prediction project"
git push
```

Sebelum `git add .`, biasakan menjalankan `git status` agar tahu file yang akan diunggah.
