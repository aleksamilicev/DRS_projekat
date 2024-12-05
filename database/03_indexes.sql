-- Indeks za kolonu Korisnicko_ime u Contact_korisnika (jedinstven)
CREATE UNIQUE INDEX idx_korisnicko_ime ON Contact_korisnika (Korisnicko_ime);

-- Indeks za kolonu Email u Contact_korisnika (jedinstven)
CREATE UNIQUE INDEX idx_email ON Contact_korisnika (Email);

-- Indeksi za pretragu korisnika po raznim poljima u Contact_korisnika
CREATE INDEX idx_korisnik_ime ON Contact_korisnika (Ime);
CREATE INDEX idx_korisnik_prezime ON Contact_korisnika (Prezime);
CREATE INDEX idx_korisnik_adresa ON Contact_korisnika (Adresa);
CREATE INDEX idx_korisnik_grad ON Contact_korisnika (Grad);

-- Indeks za jedinstven par (ID_Korisnika1, ID_Korisnika2) u tabeli Prijateljstva
CREATE UNIQUE INDEX idx_prijateljstva ON Prijateljstva (ID_Korisnika1, ID_Korisnika2);

-- Indeks za kolonu ID_Korisnika1 u tabeli Prijateljstva (za èesto pretraživanje po ID_Korisnika1)
CREATE INDEX idx_prijateljstva_korisnik1 ON Prijateljstva (ID_Korisnika1);

-- Indeks za kolonu Status u tabeli Osnovni_podaci_objave (za filtriranje objava po statusu)
CREATE INDEX idx_status_objave ON Osnovni_podaci_objave (Status);

-- Indeks za kolonu Datum_vreme_kreiranja u tabeli Sadrzaj_objave (za sortiranje objava po vremenu kreiranja)
CREATE INDEX idx_datum_vreme_kreiranja ON Sadrzaj_objave (Datum_vreme_kreiranja);

-- Indeks za kolonu Status u tabeli Osnovni_podaci_notifikacije (za filtriranje notifikacija po statusu)
CREATE INDEX idx_status_notifikacije ON Osnovni_podaci_notifikacije (Status);

-- Indeks za kolonu Datum_vreme_slanja u tabeli Sadrzaj_notifikacije (za sortiranje notifikacija po vremenu slanja)
CREATE INDEX idx_datum_vreme_slanja ON Sadrzaj_notifikacije (Datum_vreme_slanja);

-- Indeks za kolonu Blokiran u tabeli Nalog_korisnika (za pretragu blokiranih korisnika)
CREATE INDEX idx_blokiran_korisnik ON Nalog_korisnika (Blokiran);



-- Objasnjenje:
--Jedinstveni indeksi:
--
--    idx_korisnicko_ime i idx_email obezbeðuju da Korisnicko_ime i Email budu jedinstveni, što je kljuèni zahtev projekta.
--
--Indeksi za pretragu korisnika:
--
--    Dodati indeksi za èesto pretraživane kolone u tabeli Contact_korisnika.
--
--Indeksi za prijateljstva:
--
--    Jedinstveni indeks za par (ID_Korisnika1, ID_Korisnika2) osigurava da se isto prijateljstvo ne unosi dva puta.
--    Dodatni indeks na ID_Korisnika1 optimizuje pretrage po korisniku.
--
--Indeksi za objave:
--
--    idx_status_objave i idx_datum_vreme_kreiranja omoguæavaju brzo filtriranje i sortiranje objava.
--
--Indeksi za notifikacije:
--
--    idx_status_notifikacije i idx_datum_vreme_slanja optimizuju filtriranje i sortiranje notifikacija.
--
--Indeks za blokirane korisnike:
--
--    idx_blokiran_korisnik olakšava pretragu korisnika na osnovu blokiran statusa, ukljucujuci blokirane.
