# Dry Run Panel

Sanal işlem verilerini Supabase'den okuyup Streamlit üzerinde gösteren basit bir panel. Uygulama yalnızca veri okur; gerçek alım-satım emri göndermez.

## Yerel çalıştırma

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Supabase bağlantısı

Streamlit uygulama ayarlarında **Secrets** bölümüne aşağıdaki değerleri girin. Supabase URL ve `anon`/publishable key'i kaynak koduna veya GitHub'a eklemeyin.

```toml
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_OR_PUBLISHABLE_KEY"
```

Uygulama `public.dry_run` tablosundan `balance`, `closed`, `wins`, `losses` ve `recorded_at` alanlarını okur. Supabase'de tabloya erişim için uygun Data API ve RLS `SELECT` politikası yapılandırılmalıdır. Servis rolü/secret key kullanmayın; uygulama yalnızca anon/publishable key ile okuma yapmalıdır.

## Streamlit Community Cloud

1. Bu GitHub deposunu Streamlit Community Cloud'da seçin.
2. Ana dosya olarak `app.py` girin.
3. Uygulama ayarlarında **Secrets** bölümüne yukarıdaki TOML değerlerini ekleyin.
4. Deploy edin. Veriler henüz yoksa uygulama boş durum mesajı gösterir.
