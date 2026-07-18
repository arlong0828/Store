# Stride AI 無人商店

[![CI](https://github.com/arlong0828/Store/actions/workflows/ci.yml/badge.svg)](https://github.com/arlong0828/Store/actions/workflows/ci.yml)

一套以 Django 建置的智慧零售示範系統，結合 OpenCV YuNet / SFace 本機人臉辨識與 TensorFlow 商品辨識，提供刷臉登入、商品辨識、購物車及結帳流程。

## 主要功能

- 響應式商品首頁與會員介面
- 即時相機串流及人臉登入
- CNN 鞋款辨識與自動加入購物車
- Session-based 個人購物清單
- 會員資料及辨識照片管理
- YuNet + SFace 完全本機人臉辨識，不需雲端 API

## 專案結構

```text
store/                    Django 專案設定與根路由
store_app/
├── migrations/           資料庫版本
├── services/             相機、本機人臉與商品辨識服務
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
└── model/                商品與人臉辨識模型
requirements/
├── base.txt              Django 網站核心依賴
├── ai.txt                相機與 AI 辨識依賴
└── ci.txt                GitHub Actions 測試依賴
.github/workflows/ci.yml  自動化檢查與測試
```

## 本機啟動

1. 建立 Python 虛擬環境並安裝依賴：`pip install -r requirements.txt`
2. 複製 `.env.example` 的設定到執行環境；人臉辨識不需要任何 API Key。
3. 執行 `python manage.py migrate` 建立資料庫。
4. 執行 `python manage.py runserver`，前往 `http://127.0.0.1:8000/`。

人臉辨識會使用專案內的 YuNet 與 SFace ONNX 模型，照片和特徵向量都留在本機。TensorFlow 只在執行鞋款辨識時載入。

若資料庫裡已有舊會員，套用 migration 後可從原有三張照片重建本機特徵：

```bash
python manage.py rebuild_face_profiles
```

只處理一位會員可使用 `python manage.py rebuild_face_profiles --name "會員姓名"`。

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
| `FACE_MATCH_THRESHOLD` | SFace cosine 登入門檻，預設 `0.363` |
