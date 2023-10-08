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
8.10
Version 0.8

Toiminnassa
- Käyttäjä voi luoda oman käyttäjä tunnuksen ja kirjautua sisään sekä ulos.
- Jos käyttäjä nimi tai sähköposti on jo käytössä. Siitä tulee ilmoitus eikä tunnuksen luominen onnistu.
- Käyttäjä voi kommentoida topiceja ja kirjoittaa omia.
- Käyttäjä voi käyttää hakutoimintoa ja joka etsii topiceja aiheen, otsikon ja kirjoittajan mukaan.
- Topicit järjestetään tuoreuden ja sen mukaan kuinka paljon niitä on kommentoitu, kuitenkin niin että uusin näytetään aina ensin.
- Käyttäjä voi poistaa omia viestejä ja topiceja sekä muokata niitä
- Käyttäjä voi seurata aiheita ja poistaa niitä seurattavista.
- Käyttäjä voi valita että vain ne aiheet joita hän seuraa ovat näkyvissä.
- Näytetään top 5 suosituimmat topicit.
- Näytetään seurrattavat topicit
- Käyttäjällä on mahdollisuus etsiä topiceja.
- Teksti kenttiä on rajoitettu. Viesteillä yms on maksimi pituus.
- Käyttäjänimen, nimen ja sukunimen on oltava vähintään 3 merkkiä pitkä.
- Sähköpostin on sisällettävä @ merkki.
- Salansanan on oltava vähintään 5 merkkiä pitkä.

- (bug fix) Käyttäessä hakua uusin ei enää näy ellei sovi hakuun.

Tulossa
- Käyttäjä voi poistaa oman profiilinsa
- Admin käyttäjä joka voi poistaa topiceja ja viestejä
- Admin käyttäjä voi blokata käyttäjän tai sulkea kokonaan pois palvelusta
- Admin voi palauttaa käyttäjän oikeudet
- CSS tyylittely ja viimeistely.
  
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

HUOM! jos koneeltasi löytyy jo ennestään tämän sovelluksen käyttämiä tietokantoja niin ne on luultavasti poistettava ennen kuin suostuu asentamaan uudet.

5. Käynnistä sovellus.
   - $ flask run
     
TESTAUKSESTA ja MUITA HUOMIOITA
Githubissa on tiedosto "SQL_test_dada_sql" joka on siis minun tekovaiheessa olevan SQL.n kopio.(jos nyt onnistuin tekemään sen oikein) En nyt tähän hätään saanut sitä toimimaan toisella koneella mutta jos tietotaitoa riittää niin tuon voi koittaa asentaa jolloin
sovellus ei ole niin tyhjä vaan siellä on sitten paljon aiheita ja kommentointia, sekä käyttäjiä (Lähinnä lorem ipsumia ja muuta turhaa)
Kun luot tunnuksen ja kirjaudut sisään, niin aiheet näkyvät luonti järjestyksessä eli tuoreuden ja kommentoinnin mukaan kuitenkin niin että uusin on aina ensin. Uusimmat viestit eivät tarvitse niin paljoa kommentteja kuin vanhemmat viesti noustakseen kärkeen. Pisteytys toimii niin että uusin viesti saa 100 seuraavat 98,94,88,80 jne eli seuraava menettää aina 2 pistettä edellistä enemmän. Jokainen kommentti taas antaa 10 pistettä.
Voit seurata aiheita klikkaamalla oikella puolelle olevia aihealueita joita tulee sen mukaan kun niitä luodaan. Tällöin ne ilmestyvät seurattaviin. Vastaavasti voit poistaa niitä seurattavista klikkaamalla seurattavista aiheita. Eli joudut luomaan muutaman aiheen jotta sinne ilmestyy jotakin.
