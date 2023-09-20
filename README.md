# WEPSovellus
Tietokannat ja web ohjelmointi kurssi: Harjoitustyö

- HUOM! itse sovellus löytyy master puusta.

Keskustelusovellus.

Perusidea.
- Käyttäjä luo oman profiilin joka sisältää perustiedot ja mielenkiinnon kohteet.
- Käyttäjä voi muokata tai poistaa oman profiilinsa.
- Käyttäjälle suodattuu ne keskustelut jotka häntä kiinnostaa. (Mielenkiintojen mukaan)
- Käyttäjä voi luoda omia keskustelun avauksia ja rajata näkyvyyttä halutessaan. Esim. ainoastaan autoista kiinnostuneet näkevät ja voivat kommentoida julkaisua.
- Keskustelut esitetään "arvo" järjestyksessä. Milenkiinnon, tuoreuden ja sen mukaan missä käydään kovaa keskustelua. (Jonkinlainen painotus siihen mitkä merkitsevät eniten )
- Käyttäjä voi laittaa keskustelulle kirjamerkin jolloin se näytetään listassa aina ensin.
- Ylläpitäjä voi poistaa ja sulkea keskustelun
- Ylläpitäjä voi poistaa käyttäjän tai blokata tilin määräajaksi jolloin käyttäjä voi ainoastaan lukea keskusteluja

- -----------------------------------------
20.9
Version 1.0
Forumi sovellus
Käyttäjän täytyy luoda itselleen tunnuksen jotta voi kirjauta sisälle sovellukseen.
Käyttäjä luoda uutisen/aiheen johon merkitään tägi (aihe/gategoria), otsikko ja leipäteksti.
Pääsivulla näkyvissä on jutun tägi otsikko ja tekijä, sekä se kuinka monta kommenttia kyseinen uutinen on saanut.
Käyttäjä voi klikata auki mielenkiintoiset uutiset jolloin näkyviin tulee leipäteksti.
Käyttäjä voi halutessaan kommentoida aihetta.

Asennus ohjeet. Linux
1. Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
   DATABASE_URL= postgresql:///tietokannan nimi(yleensä käyttäjä nimi)
   SECRET_KEY=<salainen-avain>

Jos testaat sovellusta Ubuntu on windows tai windows alijärjestelmä linuxille niin polku voi olla eri. (Minulla oli) postgresql://tietokannan nimi:1234SQL@localhost:5432/tietokannan nimi
   
3. Aktivoi virtuaaliympäristö ja asenna tarvittavat kirjastot ja ohjelmat. (Tarkoittaa käytännössä kaikkia niitä mitä kurssin sivuilla on asennettu)
  $ python3 -m venv venv
  $ source venv/bin/activate
  (venv) $ pip install flask
  (venv) $ pip install flask-sqlalchemy
  (venv) $ pip install psycopg2
  (venv) $ pip install python-dotenv
  $ pip install -r ./requirements.txt (HUOM! joidenkin kohdalla asennus ei välttämättä onnistu mutta ohjelma toimii siitä huolimatta. Sovellus on tehty windosin alijärjestelmä linuxsilla )

4. Olettaen että myös PostgreSQL on asennettu niin luo sovelluksen tarvitsemat tieokantarakenteet.
  $ psql < schema.sql

5. Käynnistä sovellus.
   $ flask run
