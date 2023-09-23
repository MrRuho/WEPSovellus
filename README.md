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
23.9
Version 1.0

Toiminnassa
- Käyttäjä voi luoda oman käyttäjä tunnuksen ja kirjautua sisään sekä ulos.
- Jos käyttäjä nimi tai sähköposti on jo käytössä. Siitä tulee ilmoitus eikä tunnuksen luominen onnistu.
- Käyttäjä voi kommentoida topiceja ja kirjoittaa omia.
- Käyttäjä voi käyttää hakutoimintoa ja joka etsii topiceja aiheen, otsikon ja kirjoittajan mukaan.
- Topicit järjestetään tuoreiden ja sen mukaan kuinka paljon niitä on kommentoitu, kuitenkin niin että uusin näytetään aina ensin.

Tulossa
- Käyttäjä voi poistaa oman profiilinsa
- Käyttäjä voi poistaa omia viestejä ja topiceja sekä muokata niitä
- Käyttäjä voi luoda topicin joka on salasanan takana
- Admin käyttäjä joka voi poistaa topiceja ja viestejä
- Admin käyttäjä voi blokata käyttäjän tai sulkea kokonaan pois palvelusta
- Admin voi palauttaa käyttäjän oikeudet

 Puutteita
 - Tällä hetkellä missään mihin käyttäjä voi kirjoittaa ei ole mitään rajoituksia. Esim otsikko voi olla minkä pituinen vaan. Email voi olla minkä muotoinen vain. 
 - Koodi on yhdessä app.py tiedostossa
 - Ulkoasuun ei ole vielä kiinnitetty mitään huomiota

HUOM!
   Käyttäjän email osoite. Tämän oikeellisuutta ei tarkisteta millään tavalla, eikä sillä ole mitään oikeaa käyttöä. Ainoastaan profiilia luodessa ei sallita samaa email osoitetta.

ASENNUS OHJEET. Linux
1. Kloonaa tämä repositorio omalle koneellesi.
   git clone -b master https://github.com/MrRuho/WEPSovellus.git
2. siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
   - DATABASE_URL= postgresql:///tietokannan nimi(yleensä käyttäjä nimi)
   - SECRET_KEY=<salainen-avain>

Jos testaat sovellusta Ubuntu on windows tai windows alijärjestelmä linuxille niin polku voi olla eri. (Minulla oli) postgresql://tietokannan nimi:1234SQL@localhost:5432/tietokannan nimi
   
3. Aktivoi virtuaaliympäristö ja asenna tarvittavat kirjastot ja ohjelmat. (Tarkoittaa käytännössä kaikkia niitä mitä kurssin sivuilla on asennettu)
  - $ python3 -m venv venv
  - $ source venv/bin/activate
  - (venv) $ pip install flask
  - (venv) $ pip install flask-sqlalchemy
  - (venv) $ pip install psycopg2
  - (venv) $ pip install python-dotenv
  - $ pip install -r ./requirements.txt (HUOM! joidenkin kohdalla asennus ei välttämättä onnistu mutta ohjelma toimii siitä huolimatta. Sovellus on tehty windosin alijärjestelmä linuxsilla )

4. Käynnistä tietokanta (jos ei jo ole) ja Luo sovelluksen tarvitsemat tieokantarakenteet.
  - $ start-pg.sh 
  - $ psql < schema.sql

5. Käynnistä sovellus.
   - $ flask run
     
TESTAUKSESTA ja MUITA HUOMIOITA
schema.n mukana tulee valmiiksi täytettyjä tietokantoja testausta varten. Ei ehkä kaikkein suotavin tapa tehdä mutta tällä kierroksella näin. =)
Kun luot tunnuksen ja kirjaudut sisään, niin aiheet näkyvät luonti järjestyksessä (bugi) mutta jos kommentoit tai kirjoitat oman viestin niin topicit järjestyvät niin kuin on tarkoitettu. Eli tuoreuden ja kommentoinnin mukaan. Uusimmat viestit eivät tarvitse niin paljoa kommentteja kuin vanhemmat viesti noustakseen kärkeen.
