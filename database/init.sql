-- DOT SHOP Database Initialization

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Categories
INSERT INTO categories (name, slug, description) VALUES
('مد و پوشاک', 'fashion', 'لباس، کفش و اکسسوری'),
('الکترونیک', 'electronics', 'موبایل، لپ‌تاپ و لوازم جانبی'),
('خانه و آشپزخانه', 'home', 'لوازم خانگی و آشپزخانه'),
('زیبایی و سلامت', 'beauty', 'محصولات آرایشی و بهداشتی'),
('ورزش و سرگرمی', 'sports', 'لوازم ورزشی و سرگرمی')
ON CONFLICT DO NOTHING;

-- Default admin user
INSERT INTO users (email, phone, password_hash, full_name, role, is_active, is_verified) VALUES
('admin@dotshop.ir', '09123456789', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Pzm9S2', 'مدیر سیستم', 'admin', true, true)
ON CONFLICT DO NOTHING;
-- Password: admin123

COMMIT;
