-- =====================================================
-- SCHEMA SEED SCRIPT FOR SCHOLARDESKBOT (db_seed.sql)
-- =====================================================

-- 1. Seed the Universities table with 10 examples
INSERT INTO universities (name, type) VALUES
('University of Ghana', 'Public'),
('Kwame Nkrumah University of Science and Technology', 'Public'),
('University of Cape Coast', 'Public'),
('University of Development Studies', 'Public'),
('University of Education, Winneba', 'Public'),
('Ashesi University', 'Private'),
('Central University', 'Private'),
('Ghana Technology University College', 'Private'),
('Valley View University', 'Private'),
('University for Development Studies', 'Public');


-- 2. Seed the BECE Checkers table (price: 23.00 cedis)
INSERT INTO bece_checkers (pin, serial_number, price, name) VALUES
('BECEPIN1', 'BECE001', 23.00, 'BECE Checker 1'),
('BECEPIN2', 'BECE002', 23.00, 'BECE Checker 2');


-- 3. Seed the WAEC Checkers table (price: 23.00 cedis)
INSERT INTO wassce_checkers (pin, serial_number, price, name) VALUES
('WAECPIN1', 'WAEC001', 23.00, 'WAEC Checker 1'),
('WAECPIN2', 'WAEC002', 23.00, 'WAEC Checker 2');


-- 4. Seed the Nov/Dec Checkers table (price: 23.00 cedis)
INSERT INTO novdec_checkers (pin, serial_number, price, name) VALUES
('NOVPIN1', 'NOVDEC001', 23.00, 'Nov/Dec Checker 1'),
('NOVPIN2', 'NOVDEC002', 23.00, 'Nov/Dec Checker 2');



INSERT INTO university_forms (pin, serial_number, price, name) VALUES
('UPIN1', 'UNI001', 279.99, 'University Form 1'),
('UPIN2', 'UNI002', 279.99, 'University Form 2');


-- 6. Seed the College Forms table (price: 379.99 cedis)
INSERT INTO college_forms (pin, serial_number, price, name) VALUES
('CFORM1', 'COL001', 379.99, 'College Form 1'),
('CFORM2', 'COL002', 379.99, 'College Form 2');


-- 7. Seed the Nursing Forms table (price: 279.99 cedis)
INSERT INTO nursing_forms (pin, serial_number, price, name) VALUES
('NFORM1', 'NUR001', 279.99, 'Nursing Form 1'),
('NFORM2', 'NUR002', 279.99, 'Nursing Form 2');


-- 8. Seed the Stock Tracker table
-- Note: Ensure that you have a row for each category, including "university_forms"
INSERT INTO stock_tracker (category, available_stock) VALUES
('bece', 100),
('wassce', 100),
('novdec', 100),
('university_forms', 50),
('college_forms', 50),
('nursing_forms', 50);
