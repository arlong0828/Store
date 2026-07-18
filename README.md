# Stride AI 無人商店

[![CI](https://github.com/arlong0828/Store/actions/workflows/ci.yml/badge.svg)](https://github.com/arlong0828/Store/actions/workflows/ci.yml)

一套以 Django 建置的智慧零售示範系統，結合 OpenCV / TensorFlow 商品辨識與 Azure Face 會員驗證，提供刷臉登入、商品辨識、購物車及結帳流程。

## 主要功能

- 響應式商品首頁與會員介面
- 即時相機串流及人臉登入
- CNN 鞋款辨識與自動加入購物車
- Session-based 個人購物清單
- 會員資料及辨識照片管理
- Azure Face 與 Imgur 外部服務整合

## 專案結構

```text
store/                    Django 專案設定與根路由
store_app/
├── migrations/           資料庫版本
├── services/             相機、Azure、上傳及訓練整合
├── models.py             會員、商品與 Face ID 資料模型
├── urls.py               商店功能路由
└── views.py              畫面流程與 Session 狀態
templates/
├── components/           導覽、頁尾、商品卡等共用元件
├── layouts/              全站共用版型
└── pages/                各功能頁面
static/
├── css/app.css           全站樣式
├── js/app.js             選單及上傳互動
├── images/brand/         品牌標誌與 favicon
├── images/hero/          無人商店與 AI 辨識情境圖
├── media/                舊版示範資料（新上傳檔案改存 media/）
└── model/                商品辨識模型
requirements/
├── base.txt              Django 網站核心依賴
├── ai.txt                相機與 AI 辨識依賴
└── ci.txt                GitHub Actions 測試依賴
.github/workflows/ci.yml  自動化檢查與測試
```

## 本機啟動

1. 建立 Python 虛擬環境並安裝依賴：`pip install -r requirements.txt`
2. 複製 `.env.example` 的設定到執行環境，填入 Azure Face 與 Imgur 憑證。
3. 執行 `python manage.py migrate` 建立資料庫。
4. 執行 `python manage.py runserver`，前往 `http://127.0.0.1:8000/`。

首頁與一般會員頁可在未安裝 TensorFlow / Azure SDK 時使用；只有實際執行辨識或註冊訓練時才會載入相關套件。

## CI

推送 commit 或建立 Pull Request 時，GitHub Actions 會使用 Python 3.9 與 3.11 自動執行：

- Django 系統設定檢查
- Migration 完整性與套用測試
- 必要靜態資源檢查
- 所有 Django 模板編譯
- 自動化測試

也可以在 GitHub 的 **Actions → CI → Run workflow** 手動執行。

## 環境變數

| 名稱 | 用途 |
|---|---|
| `DJANGO_SECRET_KEY` | Django 簽章金鑰 |
| `DJANGO_ALLOWED_HOSTS` | 允許的主機名稱，以逗號分隔 |
| `AZURE_FACE_KEY` | Azure Face API 金鑰 |
| `AZURE_FACE_ENDPOINT` | Azure Face API 端點 |
| `IMGUR_CLIENT_ID` | 暫存辨識影像所需的 Imgur Client ID |
