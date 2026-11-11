"""Anglické texty webu J.K.FOOD.

PAIRS: dvojice (česky, anglicky) – nahrazují se v hotových českých stránkách při generování
anglické verze (en/). Když se český text na webu změní, generátor ohlásí, která dvojice
přestala sedět, a je potřeba ji tu upravit.
"""

# skupiny sortimentu (pořadí jako JK.CATS)
CATS_EN = [
    ("Pasta", "Pasta: fusilli, elbows, wide and cut noodles, pinwheels, rice-shaped pasta and tagliatelle with wild garlic."),
    ("Single spices", "Whole, crushed and ground single spices: pepper, paprika, caraway, coriander, marjoram, star anise and many more."),
    ("Seasoning blends", "Seasoning blends made to our own recipes – for chicken, fish, steak, gyros, goulash, grilling and classic Czech dishes."),
    ("Dried vegetables", "Dried onion, garlic, carrot, celery, parsley, beetroot, horseradish, spinach and vegetable mixes – flakes, cubes, granules and powder."),
    ("Blends for the meat industry", "Seasoning and combi blends for sausages, salami, frankfurters and ham, glazing injections, technological additives and decorative spices."),
    ("Dried mushrooms, fruit and nuts", "Porcini, chanterelle, shiitake, oyster mushrooms and forest mixes, almonds, hazelnuts, walnuts, raisins and dried fruit."),
    ("Stocks, soups and sauces", "Chicken, beef, vegetable and mushroom stocks, soups, sauces, gravies and marinades for canteens, restaurants and home cooking."),
    ("Potato products", "Mashed potatoes, potato dumplings, gnocchi-style halušky, potato pancakes and potato dough mixes."),
    ("Starches and more", "Potato, corn, wheat, rice and tapioca starches, garlic pastes, paprika extracts and sweet bakery mixes."),
]

# podskupiny v katalogu
SUBS_EN = {
    "Koření jednodruhové": "Single spices", "Kořenicí směsi": "Seasoning blends", "Sušená zelenina": "Dried vegetables",
    "Dekorativní koření": "Decorative spices", "Kombi směsi": "Combi blends",
    "Kořenicí směsi z přírodního koření": "Blends of natural spices",
    "Lakovací kombi směs - nástřik (šunkový program)": "Glazing combi blend – injection (ham range)",
    "Lakovací kombi směs - nástřik (uzená masa)": "Glazing combi blend – injection (smoked meat)",
    "Lakovací kombi směs - nástřik s barvivem": "Glazing combi blend – injection with colouring",
    "Ostatní směsi": "Other blends", "Technické fosfáty": "Technical phosphates",
    "Technologické náhrady masa": "Technological meat substitutes", "Technologické přísady": "Technological additives",
    "Uzené speciality": "Smoked specialities", "Vaječné náhrady": "Egg substitutes",
    "Suché plody": "Nuts and dried fruit", "Sušené houby": "Dried mushrooms",
    "Bujóny": "Stocks", "Polévky": "Soups", "Marinády": "Marinades", "Omáčky, Šťávy": "Sauces and gravies",
    "Bramborové výrobky": "Potato products", "Česneková pasta": "Garlic paste", "Ostatní": "Other",
    "Sladký program": "Sweet range", "Škroby": "Starches", "Těstoviny": "Pasta",
}

# společné části všech stránek (hlavička, patička, formulář)
COMMON = [
    ('<html lang="cs">', '<html lang="en">'),
    ("Přeskočit na obsah", "Skip to content"),
    ("J.K.FOOD Jaroslav Kostera, úvodní stránka", "J.K.FOOD Jaroslav Kostera, home page"),
    ('aria-label="Otevřít menu"', 'aria-label="Open menu"'),
    ('aria-label="Hlavní menu"', 'aria-label="Main menu"'),
    (">Sortiment</a>", ">Products</a>"),
    (">Průmysl</a>", ">Industry</a>"),
    (">Výzkum a vývoj</a>", ">Research &amp; development</a>"),
    (">O nás</a>", ">About us</a>"),
    (">Náš tým</a>", ">Our team</a>"),
    (">Kontakt</a>", ">Contact</a>"),
    ("<h3>Sortiment</h3>", "<h3>Products</h3>"),
    ("<h3>Firma</h3>", "<h3>Company</h3>"),
    ("<h3>Kontakt</h3>", "<h3>Contact</h3>"),
    (">Kariéra</a>", ">Careers (CZ)</a>"),
    (">Ke stažení</a>", ">Downloads</a>"),
    (">Ochrana osobních údajů</a>", ">Privacy policy</a>"),
    ("© 2026 Jaroslav Kostera, J.K.FOOD s.r.o. · Větřkovice 243, 747 43 Větřkovice · IČ 27780384 · DIČ CZ27780384 · zapsaná v&nbsp;obchodním rejstříku u&nbsp;Krajského soudu v&nbsp;Ostravě, sp.&nbsp;zn. C&nbsp;51605",
     "© 2026 Jaroslav Kostera, J.K.FOOD s.r.o. · Větřkovice 243, 747 43 Větřkovice, Czech Republic · Company ID 27780384 · VAT CZ27780384 · registered in the Commercial Register kept by the Regional Court in Ostrava, file C&nbsp;51605"),
    ("<address>Větřkovice 243<br>747 43 Větřkovice</address>", "<address>Větřkovice 243<br>747 43 Větřkovice<br>Czech Republic</address>"),
    # mobilní menu (JS)
    ("'Zavřít menu' : 'Otevřít menu'", "'Close menu' : 'Open menu'"),
    # hlavička: poptávka
    ('">Poptat</a>', '">Enquire</a>'),
    ('">Poptat spolupráci</a>', '">Send an enquiry</a>'),
    # patička: firma a obory
    (">Řeznictví a masný průmysl</a>", ">Meat processing</a>"),
    (">Pekařství</a>", ">Bakery</a>"),
    (">Mlékárenský průmysl</a>", ">Dairy</a>"),
    (">Snacky a pochutiny</a>", ">Snacks</a>"),
    (">Gastro a jídelny</a>", ">Food service and canteens</a>"),
    (">Private label a OEM</a>", ">Private label and OEM</a>"),
    (">Hotová jídla CHUŤ a HOT&amp;GO</a>", ">CHUŤ and HOT&amp;GO ready meals</a>"),
]

# úvodní stránka
INDEX = [
    ("Dáváme jídlu chuť. Od roku&nbsp;1996.", "We give food its flavour. Since 1996."),
    ("<strong>Potraviny a&nbsp;ingredience od receptury po sériovou výrobu.</strong> Koření, kořenicí směsi a&nbsp;dehydratované potraviny z&nbsp;vlastní výroby ve Větřkovicích pro potravinářský průmysl, gastro i&nbsp;retail.",
     "<strong>Foods and ingredients from recipe to series production.</strong> Spices, seasoning blends and dehydrated foods from our own plant in Větřkovice, Czech Republic, for the food industry, food service and retail."),
    (">Pro průmysl <span", ">For industry <span"),
    (">Naše produkty <span", ">Our products <span"),
    # pilíře a čísla
    ('<h2 class="sr" id="pil-title">Co děláme</h2>', '<h2 class="sr" id="pil-title">What we do</h2>'),
    ("<h3>Průmysl</h3><p>Ingredience, směsi a&nbsp;technologická řešení pro potravinářskou výrobu.</p>",
     "<h3>Industry</h3><p>Ingredients, blends and technological solutions for food production.</p>"),
    ("<h3>Vývoj na míru</h3><p>Od nápadu přes recepturu, testování a&nbsp;optimalizaci až po výrobu.</p>",
     "<h3>Custom development</h3><p>From the idea through recipe, testing and optimisation all the way to production.</p>"),
    ("<h3>Vlastní produkty</h3><p>Koření, směsi, dehydratované potraviny a&nbsp;hotová jídla pro retail i&nbsp;gastro.</p>",
     "<h3>Own products</h3><p>Spices, blends, dehydrated foods and ready meals for retail and food service.</p>"),
    ("<span>Tradice a&nbsp;zkušenosti od roku&nbsp;1996</span>", "<span>Tradition and experience since 1996</span>"),
    ("<span>Profesionálů, kteří rozumí surovinám i&nbsp;výrobě</span>", "<span>Professionals who understand ingredients and production</span>"),
    ("<span>Výrobní kapacita ročně</span>", "<span>Annual production capacity</span>"),
    ("<span>Certifikovaná kvalita a&nbsp;bezpečnost</span>", "<span>Certified quality and safety</span>"),
    ('alt="Misky s mletou paprikou, kurkumou, pepřem, kmínem, majoránkou, česnekem, chilli a kořenicími směsmi"', 'alt="Bowls of ground paprika, turmeric, pepper, caraway, marjoram, garlic, chilli and seasoning blends"'),
    # video
    ("Seznamte se s&nbsp;námi</h2>", "Meet us <span class=\"lang-note\">(video in Czech)</span></h2>"),
    ("Otevřít na YouTube", "Open on YouTube"),
    ('<span class="yt-label">Přehrát video</span>', '<span class="yt-label">Play video</span>'),
    ("Video se přehraje ze služby YouTube.", "The video plays from YouTube."),
    ("'Video J.K.FOOD – Seznamte se s námi (YouTube)'", "'J.K.FOOD video – Meet us (YouTube)'"),
    # sortiment
    ("Přes 490 výrobků</h2>", "Over 490 products</h2>"),
    ("Celý sortiment <span", "Full product range <span"),
    # pro firmy
    ("Dodáváme tam, kde se vaří ve velkém", "We supply wherever cooking happens at scale"),
    ("Obchodní zástupci ve všech krajích, vlastní doprava a&nbsp;směsi připravené přesně pro vaši výrobu.",
     "Sales representatives in every Czech region, our own delivery fleet and blends prepared precisely for your production."),
    ('aria-label="Odběratelé"', 'aria-label="Customers"'),
    ("Čtyři způsoby, jak s&nbsp;námi spolupracovat", "Four ways to work with us"),
    ("<h4>Obchodní zástupce ve vašem kraji</h4>", "<h4>A sales representative in your region</h4>"),
    ("Naši zástupci působí ve všech regionech Česka a&nbsp;zásobují školy, školky, nemocnice, domovy pro seniory i&nbsp;restaurace. Zboží dovezeme vlastní dopravou do 5&nbsp;pracovních dnů.",
     "Our representatives cover every region of the Czech Republic and supply schools, kindergartens, hospitals, care homes and restaurants. We deliver with our own transport within 5 working days."),
    ("Najít zástupce <span", "Find a representative <span"),
    ("<h4>Specialisté pro potravinářský průmysl</h4>", "<h4>Specialists for the food industry</h4>"),
    ("Vývoj směsí, aplikace koření a&nbsp;dehydratovaných surovin do výroby a&nbsp;veškerá technická i&nbsp;administrativní podpora.",
     "Blend development, application of spices and dehydrated ingredients in your production, and full technical and administrative support."),
    ("Do e-shopu <span", "To the e-shop <span"),
    ("<h4>Osobní odběr ve Větřkovicích</h4>", "<h4>Collection in Větřkovice</h4>"),
    ("Preferujete osobní kontakt? Navštivte nás – probereme vaše potřeby a&nbsp;připravíme zboží k&nbsp;okamžitému odběru.",
     "Prefer to meet in person? Visit us – we will discuss your needs and prepare goods for immediate collection."),
    ("Jak k&nbsp;nám <span", "How to find us <span"),
    # záložky (JS)
    (">Domluvit spolupráci</a>", ">Discuss cooperation</a>"),
    # na míru
    ("Směs přesně pro vaši výrobu", "A blend made precisely for your production"),
    ("Máte vlastní recepturu nebo hledáte novou chuť? Vyvineme ji s&nbsp;vámi a&nbsp;vyrobíme ve Větřkovicích.",
     "Have your own recipe or looking for a new flavour? We will develop it with you and produce it in Větřkovice."),
    (">Poptat vývoj směsi</a>", ">Request a custom blend</a>"),
    ("<span>nebo zavolejte <a", "<span>or call <a"),
    # o nás
    ("<h2 class=\"sr\" id=\"pribeh-title\">O nás</h2>", "<h2 class=\"sr\" id=\"pribeh-title\">About us</h2>"),
    ("„Od samého počátku založení společnosti mám jasnou představu o&nbsp;tom, jaká naše společnost má být v&nbsp;současnosti i&nbsp;v&nbsp;budoucnu.“",
     "“From the very beginning, I have had a clear vision of what our company should be – today and in the future.”"),
    ("<span>zakladatel a&nbsp;majitel</span>", "<span>founder and owner</span>"),
    ("Poznejte náš tým <span", "Meet our team <span"),
    ('aria-label="Místo pro fotografii výroby">Místo pro fotografii výroby ve Větřkovicích', 'aria-label="Placeholder for a production photo">Placeholder for a photo of our production in Větřkovice'),
    ("Jaroslav Kostera zakládá firmu a&nbsp;vyrábí koření podle vlastních receptur.", "Jaroslav Kostera founds the company and makes spices to his own recipes."),
    ("Vzniká společnost Jaroslav Kostera, J.K.FOOD s.r.o.", "The company Jaroslav Kostera, J.K.FOOD s.r.o. is established."),
    ("<div class=\"y\">[rok]</div><p>[Doplnit milník, např. nový výrobní závod ve Větřkovicích.]</p>", "<div class=\"y\">[year]</div><p>[Milestone to be added, e.g. a new production plant in Větřkovice.]</p>"),
    ("<div class=\"y\">Dnes</div><p>Přes 100 zaměstnanců a&nbsp;odběratelé po celé České republice i&nbsp;v&nbsp;zahraničí.</p>",
     "<div class=\"y\">Today</div><p>More than 100 employees and customers across the Czech Republic and abroad.</p>"),
    # e-shop
    # reference
    ("Důvěřují nám", "Trusted by"),
    ("Naše koření a&nbsp;směsi používají výrobci, jídelny i&nbsp;restaurace po celé České republice.", "Our spices and blends are used by manufacturers, canteens and restaurants across the Czech Republic."),
    ("[Název odběratele]", "[Customer name]"),
    ('<p class="ref-type">Masná výroba</p>', '<p class="ref-type">Meat processing</p>'),
    ('<p class="ref-type">Školní jídelna</p>', '<p class="ref-type">School canteen</p>'),
    ('<p class="ref-type">Nemocnice</p>', '<p class="ref-type">Hospital</p>'),
    ('<p class="ref-type">Restaurace</p>', '<p class="ref-type">Restaurant</p>'),
    ('<p class="ref-type">Pekárna</p>', '<p class="ref-type">Bakery</p>'),
    ('<p class="ref-type">Domov pro seniory</p>', '<p class="ref-type">Care home</p>'),
    ('aria-label="Reference – posouvejte šipkami vlevo a vpravo"', 'aria-label="References – scroll with the left and right arrow keys"'),
    ('aria-label="Pozastavit posouvání referencí"', 'aria-label="Pause the references"'),
    ("'Spustit posouvání referencí' : 'Pozastavit posouvání referencí'", "'Play the references' : 'Pause the references'"),
    ('aria-label="Předchozí reference"', 'aria-label="Previous reference"'),
    ('aria-label="Další reference"', 'aria-label="Next reference"'),
    # kontakt
    ('<h2 class="h2" id="kontakt-title">Napište nám</h2>', '<h2 class="h2" id="kontakt-title">Get in touch</h2>'),
    ("Připravíme nabídku, pošleme vzorky nebo navrhneme směs na míru.", "We will prepare an offer, send samples or propose a custom blend. We are happy to communicate in English."),
    ("<address class=\"addr\">Jaroslav Kostera, J.K.FOOD s.r.o.<br>Větřkovice 243, 747 43 Větřkovice</address>",
     "<address class=\"addr\">Jaroslav Kostera, J.K.FOOD s.r.o.<br>Větřkovice 243, 747 43 Větřkovice, Czech Republic</address>"),
    ("<span>obchodní ředitel – nabídky a&nbsp;spolupráce</span>", "<span>sales director – offers and cooperation</span>"),
    ("<span>vedoucí výroby – směsi na míru, technologie</span>", "<span>production manager – custom blends, technology</span>"),
    ("<span>majitel</span>", "<span>owner</span>"),
    ('Jméno a příjmení <span class="req"', 'Full name <span class="req"'),
    ('<label for="f-firm">Firma</label>', '<label for="f-firm">Company</label>'),
    ('<label for="f-tel">Telefon</label>', '<label for="f-tel">Phone</label>'),
    ('<label for="f-type">Mám zájem o</label>', '<label for="f-type">I am interested in</label>'),
    ("<option>Nabídku sortimentu</option>", '<option value="Nabídku sortimentu">A product offer</option>'),
    ("<option>Vzorky</option>", '<option value="Vzorky">Samples</option>'),
    ("<option>Vývoj směsi na míru</option>", '<option value="Vývoj směsi na míru">A custom blend</option>'),
    ("<option>Něco jiného</option>", '<option value="Něco jiného">Something else</option>'),
    ('Zpráva <span class="req"', 'Message <span class="req"'),
    ('<label for="f-web">Nevyplňujte</label>', '<label for="f-web">Leave empty</label>'),
    ('<input type="hidden" name="produkt" id="f-prod">', '<input type="hidden" name="produkt" id="f-prod">\n          <input type="hidden" name="lang" value="en">'),
    ('<span class="lbl">Odeslat poptávku</span>', '<span class="lbl">Send enquiry</span>'),
    ("Pole s&nbsp;<span class=\"req\">*</span> jsou povinná. Údaje použijeme jen k&nbsp;vyřízení vaší poptávky (<a href=\"ochrana-osobnich-udaju.html\">ochrana osobních údajů</a>).",
     "Fields marked <span class=\"req\">*</span> are required. We use your details only to handle your enquiry (<a href=\"ochrana-osobnich-udaju.html\">privacy policy</a>)."),
    ("<h3>Děkujeme, poptávka odešla.</h3>", "<h3>Thank you, your enquiry has been sent.</h3>"),
    ("Ozveme se vám co nejdříve, obvykle do jednoho pracovního dne. Potvrzení jsme poslali na váš e-mail.",
     "We will get back to you as soon as possible, usually within one working day. A confirmation has been sent to your e-mail."),
    (">Poslat další poptávku</button>", ">Send another enquiry</button>"),
    # formulář (JS)
    ("'Dobrý den, mám zájem o výrobek: '", "'Hello, I am interested in the product: '"),
    ("'Vyplňte prosím jméno.'", "'Please enter your name.'"),
    ("'Vyplňte prosím e-mail.'", "'Please enter your e-mail.'"),
    ("'Zadejte prosím platný e-mail.'", "'Please enter a valid e-mail address.'"),
    ("'Telefon může obsahovat jen čísla, mezery a znak +.'", "'The phone number may contain only digits, spaces and +.'"),
    ("'Napište nám prosím, o co máte zájem.'", "'Please tell us what you are interested in.'"),
    ("'Poptávka: '", "'Enquiry: '"),
    ("'Odeslat poptávku e-mailem'", "'Send the enquiry by e-mail'"),
    ("note.append(a, ' nebo zavolejte ');", "note.append(a, ' or call ');"),
    ("'Odesílám…' : 'Odeslat poptávku'", "'Sending…' : 'Send enquiry'"),
    ("'Poptávku se teď nepodařilo odeslat.'", "'Your enquiry could not be sent right now.'"),
    ("'Nepodařilo se spojit se serverem.'", "'Could not connect to the server.'"),
    ("fail('Poptávku se nepodařilo odeslat.')", "fail('Your enquiry could not be sent.')"),
    # verze B2B: úvod, proč my, postup, sortiment, e-shop
    ('<span>Vyvíjíme.</span> <span>Vyrábíme.</span> <span class="accent">Dodáváme.</span>',
     '<span>We develop.</span> <span>We produce.</span> <span class="accent">We deliver.</span>'),
    ('alt="Proud kořenicí směsi se sype z nerezové násypky do průmyslového míchacího stroje"', 'alt="A stream of seasoning blend pouring from a stainless hopper into an industrial mixer"'),
    ("Proč spolupracovat s&nbsp;J.K.FOOD", "Why work with J.K.FOOD"),
    ("<h3>Zkušenosti napříč obory</h3><p>Od roku 1996 dodáváme masné výrobě, pekárnám, mlékárnám, výrobcům snacků i&nbsp;velkým kuchyním.</p>",
     "<h3>Experience across sectors</h3><p>Since 1996 we have supplied meat processors, bakeries, dairies, snack producers and large kitchens.</p>"),
    ("<h3>Rozumíme výrobě</h3><p>Víme, jak se suroviny chovají při dávkování, zpracování i&nbsp;skladování.</p>",
     "<h3>We understand production</h3><p>We know how ingredients behave during dosing, processing and storage.</p>"),
    ("<h3>Kvalita a opakovatelnost</h3><p>Stejná chuť, barva a&nbsp;sypkost v&nbsp;každé šarži.</p>",
     "<h3>Quality and consistency</h3><p>The same taste, colour and flowability in every batch.</p>"),
    ("<h3>Flexibilní přístup</h3><p>Receptura, balení i&nbsp;dodávky podle vašich potřeb.</p>",
     "<h3>Flexible approach</h3><p>Recipe, packaging and deliveries tailored to your needs.</p>"),
    ("<h3>Analýza potřeb</h3><p>Probereme váš výrobek, technologii, požadovanou chuť i&nbsp;cenu.</p>",
     "<h3>Needs analysis</h3><p>We discuss your product, technology, target taste and price.</p>"),
    ("<h3>Návrh řešení</h3><p>Navrhneme suroviny nebo směs a&nbsp;připravíme vzorky.</p>",
     "<h3>Proposed solution</h3><p>We propose ingredients or a blend and prepare samples.</p>"),
    ("<h3>Testování a ladění</h3><p>Vzorky vyzkoušíte ve své výrobě, podle výsledků je doladíme.</p>",
     "<h3>Testing and fine-tuning</h3><p>You test the samples in your production and we fine-tune them.</p>"),
    ("<h3>Výrobní standard</h3><p>Recepturu zafixujeme, aby každá šarže byla stejná.</p>",
     "<h3>Production standard</h3><p>We fix the recipe so that every batch is the same.</p>"),
    ("<h3>Dodávky a podpora</h3><p>Pravidelné dodávky vlastní dopravou a&nbsp;technická podpora.</p>",
     "<h3>Delivery and support</h3><p>Regular deliveries by our own transport and technical support.</p>"),
    (">Výzkum a vývoj <span", ">Research &amp; development <span"),
    ("<h4>Výroba pod vaší značkou</h4><p>Koření a&nbsp;směsi vyrobíme a&nbsp;zabalíme pod značkou vašeho obchodu nebo firmy.</p>",
     "<h4>Production under your brand</h4><p>We produce and pack spices and blends under the brand of your shop or company.</p>"),
    (">Private label a OEM <span", ">Private label and OEM <span"),
    ("Suroviny pro výrobu i&nbsp;velké kuchyně. Balení a&nbsp;množství podle vaší spotřeby, vzorky na vyžádání.",
     "Ingredients for food production and large kitchens. Pack sizes and quantities to match your consumption, samples on request."),
    ("vřetena, kolínka, široké a&nbsp;řezané nudle", "fusilli, elbows, wide and cut noodles"),
    ("pepř, paprika, kmín, majoránka – celé, drcené, mleté", "pepper, paprika, caraway, marjoram – whole, crushed, ground"),
    ("gulášové, grilovací, na kuře, gyros, svíčkovou", "goulash, grill, chicken, gyros and more"),
    ("cibule, česnek, mrkev, celer – plátky, kostky, pudr", "onion, garlic, carrot, celery – flakes, cubes, powder"),
    ("kombi směsi, lakovací nástřiky, technologické přísady", "combi blends, glazing injections, technological additives"),
    ("hřib, liška, shiitake, ořechy a&nbsp;sušené ovoce", "porcini, chanterelle, shiitake, nuts and dried fruit"),
    ("bujóny, polévky, omáčky a&nbsp;marinády pro velké kuchyně", "stocks, soups, sauces and marinades for large kitchens"),
    ("kaše, knedlíky, halušky, bramborák", "mashed potatoes, dumplings, gnocchi-style halušky, potato pancakes"),
    ("škroby, česnekové pasty, paprikové výtažky", "starches, garlic pastes, paprika extracts"),
    (">Vlastní značky<", ">Own brands<"),
    (">Hotová jídla v kelímku CHUŤ a HOT&amp;GO<", ">CHUŤ and HOT&amp;GO ready meals in a cup<"),
    ("stačí zalít horkou vodou – kompletní jídlo za pár minut", "just add hot water – a complete meal in a few minutes"),
    ('aria-label="E-shop pro domácnosti"', 'aria-label="E-shop for households"'),
    ("<b>Nakupujete pro domácnost?</b> Naše koření a&nbsp;směsi v&nbsp;menších baleních najdete v&nbsp;e-shopu.",
     "<b>Shopping for your household?</b> Our spices and blends in smaller packs are available in our e-shop (in Czech)."),
    # záložky oborů (JS)
    ("'Dobrý den, jsme z oboru ' + obor + '.\\n\\n'", "'Hello, our sector: ' + obor + '.\\n\\n'"),
    ("name: 'Masný průmysl', title: 'Chuť, barva a konzistence pod kontrolou',\n      text: 'Kořenicí a technologické směsi přizpůsobené masné výrobě a vaší technologii.',\n      pts: ['Stabilní chuť a barva', 'Navážení na výrobní dávku', 'Technologické postupy ke kombi směsím']",
     "name: 'Meat processing', title: 'Taste, colour and texture under control',\n      text: 'Seasoning and technological blends tailored to meat production and your technology.',\n      pts: ['Stable taste and colour', 'Pre-weighed for your production batch', 'Technological procedures for combi blends']"),
    ("name: 'Pekařství', title: 'Funkční suroviny pro pekařskou výrobu',\n      text: 'Suroviny a směsi pro rovnoměrné rozložení chuti, stabilní strukturu a jednoduchou aplikaci.',\n      pts: ['Koření a semínka do pečiva', 'Stabilní receptury', 'Opakovatelné výsledky']",
     "name: 'Bakery', title: 'Functional ingredients for bakery production',\n      text: 'Ingredients and blends for even flavour distribution, stable structure and easy application.',\n      pts: ['Spices and seeds for baked goods', 'Stable recipes', 'Repeatable results']"),
    ("name: 'Mlékárny', title: 'Stabilní chuť v mléčných výrobcích',\n      text: 'Suroviny a směsi tam, kde je důležitá jemnost chuti, stabilita při zpracování a kontrola složení.',\n      pts: ['Pro různé teplotní režimy', 'Konzistentní senzorický výsledek', 'Sušená zelenina a bylinky']",
     "name: 'Dairy', title: 'Stable taste in dairy products',\n      text: 'Ingredients and blends where delicate flavour, processing stability and control of composition matter.',\n      pts: ['For various temperature regimes', 'Consistent sensory result', 'Dried vegetables and herbs']"),
    ("name: 'Snacky a pochutiny', title: 'Intenzivní chuť a efektivní aplikace',\n      text: 'Směsi pro rychlou aplikaci a rovnoměrné ochucení snacků a pochutin.',\n      pts: ['Efektivní výroba', 'Stabilní chuťový profil', 'Minimální rozdíly mezi šaržemi']",
     "name: 'Snacks', title: 'Intense flavour, efficient application',\n      text: 'Blends for fast application and even seasoning of snacks.',\n      pts: ['Efficient production', 'Stable flavour profile', 'Minimal batch-to-batch variation']"),
    ("name: 'Gastro a jídelny', title: 'Spolehlivý dodavatel pro velké kuchyně',\n      text: 'Bujóny, polévky, omáčky, koření a sušená zelenina v gastro baleních pro jídelny, restaurace i catering.',\n      pts: ['Gastro balení', 'Dodávky vlastní dopravou', 'Obchodní zástupce ve vašem kraji']",
     "name: 'Food service', title: 'A reliable supplier for large kitchens',\n      text: 'Stocks, soups, sauces, spices and dried vegetables in catering packs for canteens, restaurants and caterers.',\n      pts: ['Catering packs', 'Delivery by our own transport', 'A sales representative in your region']"),
    ("name: 'Private label a OEM', title: 'Vývoj a výroba pod vaší značkou',\n      text: 'Pro průmyslové a obchodní partnery vyvíjíme receptury, optimalizujeme je pro výrobu a dlouhodobě dodáváme.',\n      pts: ['Technické konzultace', 'Standardizace výroby', 'Logistická podpora']",
     "name: 'Private label and OEM', title: 'Development and production under your brand',\n      text: 'For industrial and retail partners we develop recipes, optimise them for production and supply long-term.',\n      pts: ['Technical consultations', 'Production standardisation', 'Logistics support']"),
    (">Více pro váš obor <span", ">More for your sector <span"),
]

# katalog (sortiment)
CATALOG = [
    ('placeholder="Hledat, např. pepř, guláš, šunka…"', 'placeholder="Search Czech names, e.g. pepř, guláš…"'),
    ('<label class="sr" for="q">Hledat výrobek</label>', '<label class="sr" for="q">Search products</label>'),
    ('aria-label="Vymazat hledání"', 'aria-label="Clear search"'),
    ('aria-label="Skupiny výrobků"', 'aria-label="Product groups"'),
    (">Vše</a>", ">All</a>"),
    ("<p class=\"cat-empty-title\">Tohle jsme v&nbsp;sortimentu nenašli.</p>", "<p class=\"cat-empty-title\">We could not find that in our range.</p>"),
    ("<p>Zkuste jiné slovo, nebo nám napište – směs vám rádi připravíme na míru.</p>", "<p>Try another word or write to us – we will be happy to prepare a custom blend for you.</p>"),
    (">Napsat poptávku</a>", ">Send an enquiry</a>"),
    ("Hledáte vlastní chuť?", "Looking for your own flavour?"),
    ("<p>Kořenicí směs vyvineme přesně podle vaší výroby a&nbsp;receptury.</p>", "<p>We will develop a seasoning blend precisely for your production and recipe.</p>"),
    ("Nakoupit v&nbsp;e-shopu <span", "Visit the e-shop (CZ) <span"),
    ('aria-label="Drobečková navigace"', 'aria-label="Breadcrumbs"'),
    # JS
    ("const plural = n => n === 1 ? 'výrobek' : n >= 2 && n <= 4 ? 'výrobky' : 'výrobků';", "const plural = n => n === 1 ? 'product' : 'products';"),
    ("'Nalezeno: ' + shown", "'Found: ' + shown"),
]

# tým
TEAM = {
    "intro": "The people behind every blend we make in Větřkovice. Meet those you will work with most often.",
    "groups": {"Vedení firmy": "Management", "Obchodní zástupci": "Sales representatives",
               "Výroba a vývoj": "Production and development", "Kancelář a expedice": "Office and dispatch"},
    "popis": {"Ozvěte se zástupci pro váš kraj – připraví nabídku, přiveze vzorky a domluví pravidelné dodávky.":
              "Contact the representative for your region – they will prepare an offer, bring samples and arrange regular deliveries."},
    "roles": {"majitel": "owner", "zakladatel a majitel": "founder and owner", "obchodní ředitel": "sales director",
              "vedoucí výroby": "production manager", "obchodní zástupce": "sales representative",
              "[Jméno a příjmení]": "[Name]", "[kraj]": "[region]", "[pozice, např. obchodní ředitel]": "[position]",
              "[vedoucí výroby]": "[production manager]", "[technolog, vývoj směsí na míru]": "[technologist, custom blend development]",
              "[objednávky a fakturace]": "[orders and invoicing]"},
}


# ---------------------------------------------------------------- stránky pro firmy (Průmysl, obory, vývoj, hotová jídla)
# české soubory → anglické
B2B_FILES = {
    "prumysl.html": "industry.html", "vyzkum-a-vyvoj.html": "research-development.html", "hotova-jidla.html": "ready-meals.html",
    "masny-prumysl.html": "meat-processing.html", "pekarstvi.html": "bakery.html", "mlekarny.html": "dairy.html",
    "snacky-a-pochutiny.html": "snacks.html", "gastro-a-jidelny.html": "food-service.html", "privatni-znacka.html": "private-label.html",
}

B2B_UI = {
    "home": "Home", "industry": "Industry",
    "focus_sr": "What we focus on", "focus_lead": "We focus on:",
    "offer": "What we do for you", "cats": "Typical products", "all": "Full product range",
    "steps": "How we work together", "others": "Other sectors",
    "cta_title": "We will send you samples", "cta_text": "Tell us what you produce and what you are looking for – we will prepare samples and an offer.",
    "cta_enquire": "Send an enquiry", "cta_samples": "Request samples",
    "why": "Why work with J.K.FOOD", "count": "products",
}

STEPS5_EN = [("Needs analysis", "We discuss your product, technology, target taste and price."),
             ("Proposed solution", "We propose ingredients or a blend and prepare samples."),
             ("Testing and fine-tuning", "You test the samples in your production and we fine-tune them."),
             ("Production standard", "We fix the recipe so that every batch is the same."),
             ("Delivery and support", "Regular deliveries by our own transport and technical support.")]

WHY_EN = [("Experience across sectors", "Since 1996 we have supplied meat processors, bakeries, dairies, snack producers and large kitchens."),
          ("We understand production", "We know how ingredients behave during dosing, processing and storage."),
          ("Quality and consistency", "The same taste, colour and flowability in every batch."),
          ("Flexible approach", "Recipe, packaging and deliveries tailored to your needs.")]

V2_EX_EN = {
    "testoviny": "fusilli, elbows, wide and cut noodles",
    "koreni": "pepper, paprika, caraway, marjoram – whole, crushed, ground",
    "smesi": "goulash, grill, chicken, gyros and more",
    "zelenina": "onion, garlic, carrot, celery – flakes, cubes, powder",
    "maso": "combi blends, glazing injections, technological additives",
    "houby": "porcini, chanterelle, shiitake, nuts and dried fruit",
    "polevky": "stocks, soups, sauces and marinades for large kitchens",
    "brambory": "mashed potatoes, dumplings, potato pancakes",
    "skroby": "starches, garlic pastes, paprika extracts",
}

OBORY_EN = {
    "masny-prumysl.html": dict(
        name="Meat processing", nav="Meat processing",
        title="Seasoning and combi blends for meat processing | J.K.FOOD",
        desc="Seasoning and technological blends for butchers and meat producers: sausages, salami, frankfurters, ham. Stable taste and colour, precise dosing, pre-weighed batches.",
        h1="Butchers and meat processing", tag="Taste, colour and texture under control",
        intro="For butchers and meat producers we supply seasoning and technological blends tailored to the specific requirements of meat production.",
        focus=["stable taste and colour", "compatibility with your production technology", "simple and precise dosing"],
        offer=[("Blends to your recipe", "We develop a blend for you, or take over your recipe and produce it in consistent quality."),
               ("Pre-weighed for your batch", "We mix spices, starches and technological additives directly for your bowl-cutter batch. No weighing, no dust."),
               ("Technological procedures", "We supply technological procedures for combi blends and help when introducing a new product."),
               ("Packaging and batch labelling", "Pack sizes to match your consumption, batch number on every pack, EAN code on request.")]),
    "pekarstvi.html": dict(
        name="Bakery", nav="Bakery",
        title="Spices and blends for bakeries | J.K.FOOD",
        desc="Spices, seeds, seasoning blends and dried vegetables for bakery production. Even flavour distribution, stable recipes, easy application.",
        h1="Bakery", tag="Functional ingredients for bakery production",
        intro="We offer bakeries ingredients and blends that support even flavour distribution, a stable structure and easy application in production.",
        focus=["simpler handling of flavouring ingredients", "stable recipes", "repeatable results in production"],
        offer=[("Spices and seeds for baked goods", "Caraway, coriander, fennel and other spices, whole or ground."),
               ("Dried vegetables", "Onion, garlic, peppers and other vegetables as flakes, cubes or granules."),
               ("Custom blends", "We prepare a blend for your product – from savoury bakery to filled products."),
               ("Pack sizes for your volume", "We adapt the pack size to your consumption.")]),
    "mlekarny.html": dict(
        name="Dairy", nav="Dairy",
        title="Ingredients and blends for dairies | J.K.FOOD",
        desc="Spices, seasoning blends and dried vegetables for dairy products – spreads, cheeses, dressings. Delicate flavour, processing stability, controlled composition.",
        h1="Dairy industry", tag="Stable taste and functionality in dairy products",
        intro="For dairies we supply ingredients and blends for applications where delicate flavour, processing stability and controlled composition matter.",
        focus_lead="Our solutions are designed to:",
        focus=["respect the technological requirements of dairy production", "work across different temperature regimes", "support a consistent sensory result"], offer=[]),
    "snacky-a-pochutiny.html": dict(
        name="Snacks", nav="Snacks",
        title="Seasoning blends for snacks | J.K.FOOD",
        desc="Seasoning and flavouring blends for snack producers: fast application, even seasoning, a stable flavour profile from batch to batch.",
        h1="Snacks", tag="Intense flavour, efficient application",
        intro="For snack producers we offer blends designed for fast application and even seasoning.",
        focus_lead="Our solutions are designed for:",
        focus=["production efficiency", "a stable flavour profile", "minimal batch-to-batch variation"], offer=[]),
    "gastro-a-jidelny.html": dict(
        name="Food service", nav="Food service and canteens",
        title="Spices, stocks and soups for canteens and food service | J.K.FOOD",
        desc="Stocks, soups, sauces, seasoning blends and dried vegetables in catering packs for school and hospital canteens, restaurants, hotels and caterers.",
        h1="Food service and canteens", tag="A reliable supplier for large kitchens",
        intro="Stocks, soups, sauces, spices and dried vegetables in catering packs for school, hospital and social catering, restaurants, hotels and caterers.",
        focus=[],
        offer=[("Catering packs", "Large packs of spices, blends and semi-finished products that are easy to work with in a large kitchen."),
               ("Regular deliveries", "We deliver with our own transport, usually within 5 working days (Czech Republic)."),
               ("A sales representative in your region", "Personal contact, advice on the range and help with orders."),
               ("Ready blends and ingredients", "Blends for meat, fish and vegetables, potato products, pasta and dried mushrooms.")]),
    "privatni-znacka.html": dict(
        name="Private label and OEM", nav="Private label and OEM",
        title="Private label and OEM – spices and blends under your brand | J.K.FOOD",
        desc="Private label and OEM cooperation: recipe development, optimisation for production, standardisation and long-term supply of spices and blends under the partner's brand.",
        h1="Private label and OEM", tag="Development and production to order",
        intro="We offer industrial and retail partners private label and OEM cooperation. We develop recipes, optimise them for production and supply long-term.",
        focus_lead="Our cooperation includes:",
        focus=["technical consultations", "development and adjustment of composition", "production standardisation", "logistics support"], offer=[]),
}

PRUMYSL_EN = dict(
    title="Industry – ingredients and blends for food manufacturers | J.K.FOOD",
    desc="Dehydrated ingredients, seasoning and technological blends for the food industry: meat processing, bakery, dairy, snacks, private label and OEM.",
    h1="Solutions for food manufacturers and processors",
    intro="We supply ingredients and blends for the food industry, where consistent quality, repeatable taste and functionality in the production process are key. We work with manufacturers across food sectors.",
    tag="A reliable partner for industrial applications", h2="Dehydrated ingredients and technological blends",
    p="For industrial producers we supply dehydrated ingredients, seasoning and technological blends that allow precise dosing, stable taste and easy integration into production lines. Every solution is adapted to the specific technology, production process and desired result.",
    lead="Our solutions help to:", pts=["reduce dependence on seasonal raw materials", "simplify production processes", "ensure the same quality across batches"],
    alt="A worker operating an industrial mixer with a seasoning blend", sectors="Sectors we supply",
    cta_title="Contact for industrial partners",
    cta_text="Do you have specific requirements or are you looking for a reliable supplier for your production? We will be glad to discuss the options with you.",
    obor="Industry")

VYVOJ_EN = dict(
    title="Research and development of custom seasoning blends | J.K.FOOD",
    desc="Our own development facilities: custom recipes, adjustments of taste and composition, batch stability and introduction into series production. Samples for testing.",
    h1="Research and development",
    intro="Development is a natural part of J.K.FOOD. In our own development facilities we create and test recipes so that they meet requirements for taste, functionality and long-term stability.",
    tag="Consistent quality starts with development", h2="What our development covers",
    p="We develop every product with its real use in mind – in production, food service and retail. We monitor technological behaviour, sensory properties and the repeatability of the result. We do not develop for the drawer, but for production.",
    lead="We focus in particular on:", pts=["taste, aroma and colour stability", "homogeneity of blends and batch stability", "dosing, flowability and miscibility", "product behaviour during processing and storage"],
    alt="Laboratory: a seasoning blend sample on a laboratory scale, test tubes with spice samples",
    h2b="Custom development and cooperation",
    pb="We work with manufacturers, food service and private label partners. We create new products and adjust existing recipes to a specific brief, technology and target price.",
    cards=[("Custom blend development", "A new flavour based on your brief and technology."),
           ("Taste and composition adjustments", "We fine-tune an existing recipe – taste, composition and price."),
           ("Consistent quality as you grow", "We prepare the recipe so that it works at higher volumes too."),
           ("Introduction into series production", "We help with the transition from sample to regular production.")],
    quote="We are not just an ingredient supplier. We are a partner who understands ingredients, technology and production.",
    cta_title="Do you have a specific brief?", cta_text="We will be glad to discuss your project and prepare samples for testing.",
    cta_btn="Enquire about development", obor="Custom development")

JIDLA_EN = dict(
    title="CHUŤ and HOT&GO ready meals in a cup | J.K.FOOD",
    desc="CHUŤ and HOT&GO ready meals in a cup: just add hot water. For shops, offices, workplaces and travel.",
    h1="CHUŤ and HOT&GO ready meals in a cup",
    intro="Our own range of ready meals for quick and simple preparation. Reliable taste, convenience and the same result wherever you are.",
    tag="A reliable solution when time matters", h2="A complete meal in a few minutes",
    p="The CHUŤ and HOT&amp;GO ready meals in a cup are designed for quick and simple preparation. Just add hot water and the meal is ready in a few minutes – at home, at work or on the go.",
    lead="Every cup:", pts=["is a complete ready meal", "has a clear and simple preparation method", "gives the same taste every time", "needs no extra ingredients or equipment"],
    ph_hero="Photo of the CHUŤ and HOT&amp;GO range", ph_hero_label="Placeholder for a photo of CHUŤ and HOT&amp;GO ready meals",
    ph_item="Photo of the cup", ph_item_sub="name · weight · preparation", h_types="Varieties and packaging",
    h_b2b="For trade partners",
    pb="Ready meals in a cup are easy to store, carry and sell. They suit places where customers need a quick and reliable meal – offices and workplaces, students and travel.",
    cards=[("Quick preparation", "No cooking – just hot water."), ("No extra dishes", "The meal is prepared and served directly in the cup."),
           ("Easy storage", "The cups are easy to store, carry and display."), ("A full meal portion", "Every cup is a full portion.")],
    cta_title="Ready meals for your range", cta_text="Interested in CHUŤ and HOT&amp;GO ready meals for your shop or business? Write to us.",
    cta_btn="Enquire about ready meals", obor="CHUŤ and HOT&GO ready meals")

# ---------------------------------------------------------------- ochrana osobních údajů a cookies
B2B_FILES.update({"ochrana-osobnich-udaju.html": "privacy.html", "cookies.html": "cookies.html"})

_FILL = '<mark class="fill">[to be completed: {}]</mark>'
_CTRL = ("Jaroslav Kostera, J.K.FOOD s.r.o., Větřkovice 243, 747 43 Větřkovice, Czech Republic, Company ID 27780384, "
         "registered in the Commercial Register kept by the Regional Court in Ostrava, file C 51605")
LEGAL_EN = {
    "privacy": dict(
        title="Privacy policy | J.K.FOOD",
        desc="How J.K.FOOD processes personal data from the enquiry form, e-mail and CVs, and what your rights are.",
        h1="Privacy policy",
        intro="How we process your personal data on kostera.cz and what rights you have.",
        body=[
            ("Data controller", f"<p>{_CTRL}.</p><p>Contact for personal data matters: "
             '<a href="mailto:kostera@kostera.cz">kostera@kostera.cz</a>, <a href="tel:+420556310205">+420 556 310 205</a>.</p>'),
            ("What data we process and why",
             "<h3>Enquiry form and direct contact</h3>"
             "<p>Name, company, e-mail, phone, your message and, where relevant, the product or sector you are interested in.</p>"
             "<ul><li><b>Purpose:</b> handling your enquiry, preparing an offer and follow-up communication.</li>"
             "<li><b>Legal basis:</b> steps prior to entering into a contract at your request (Art. 6(1)(b) GDPR) and our legitimate "
             "interest in answering your question (Art. 6(1)(f) GDPR).</li></ul>"
             "<h3>CVs and job applications</h3>"
             "<p>Data you send us in your CV or e-mail.</p>"
             "<ul><li><b>Purpose:</b> recruitment for a vacancy.</li>"
             "<li><b>Legal basis:</b> steps prior to entering into an employment contract (Art. 6(1)(b) GDPR); longer retention only with your consent.</li></ul>"
             "<h3>Technical data</h3>"
             "<p>When you visit the website, the server records technical data (IP address, time, page viewed, browser type). "
             "To protect the form against abuse we keep a hash of your IP address for 10 minutes.</p>"
             "<ul><li><b>Purpose:</b> operation and security of the website.</li><li><b>Legal basis:</b> legitimate interest (Art. 6(1)(f) GDPR).</li></ul>"),
            ("How long we keep data",
             f"<ul><li>Enquiries and communication: {_FILL.format('e.g. 3 years from the last contact')}; if we conclude a contract, for the period required by law.</li>"
             f"<li>CVs: until the end of the recruitment process, with your consent {_FILL.format('e.g. 1 year')}.</li>"
             f"<li>Server logs: {_FILL.format('according to hosting settings, usually 30–90 days')}.</li></ul>"),
            ("Who we share data with",
             f"<p>We do not sell your data or pass it on for marketing. It is processed only by our employees and by suppliers who run "
             f"our website and e-mail ({_FILL.format('name of the hosting and e-mail provider')}).</p>"
             "<p>The video on the home page is loaded from YouTube (Google Ireland Limited) – see "
             '<a href="cookies.html">Cookies</a>. Google may transfer data to the USA under the EU-US Data Privacy Framework.</p>'),
            ("Your rights",
             "<p>You have the right of access to your data, to rectification or erasure, to restriction of processing, to data portability, "
             "to object to processing based on legitimate interest and to withdraw consent where given. "
             'Just write to <a href="mailto:kostera@kostera.cz">kostera@kostera.cz</a>.</p>'
             "<p>If you believe we process your data unlawfully, you may lodge a complaint with the Czech Office for Personal Data Protection "
             '(<a href="https://uoou.gov.cz" target="_blank" rel="noopener">uoou.gov.cz</a>).</p>'),
        ],
        note=f"Effective from {_FILL.format('date')}. This text is a template prepared for the website – the company will verify it before launch."),
    "cookies": dict(
        title="Cookies | J.K.FOOD",
        desc="Which cookies and browser storage kostera.cz uses. No advertising or analytics cookies.",
        h1="Cookies",
        intro="kostera.cz does not use advertising or analytics cookies and does not track your visit.",
        body=[
            ("What the website stores in your browser",
             '<div class="legal-table"><table><thead><tr><th>Name</th><th>Purpose</th><th>Duration</th></tr></thead><tbody>'
             "<tr><td><code>jkadmin</code></td><td>Login to the administration – website administrators only.</td><td>until the browser is closed</td></tr>"
             "</tbody></table></div>"
             "<p>Apart from this, the website stores nothing in your browser.</p>"),
            ("YouTube video",
             "<p>The home page contains a video from YouTube (Google). It loads once you start browsing the page and plays automatically, "
             "muted, when you reach it. It is played from youtube-nocookie.com (privacy-enhanced mode), but YouTube may still store cookies "
             "and similar data in your browser and process your IP address – according to "
             '<a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Google\'s privacy policy</a>.</p>'
             "<p>If you do not want this, you can block third-party content in your browser or watch the video directly on YouTube.</p>"),
            ("How to delete cookies",
             "<p>You can delete cookies and site data at any time in your browser settings (usually Settings → Privacy → Clear browsing data).</p>"
             '<p>More about personal data processing: <a href="ochrana-osobnich-udaju.html">Privacy policy</a>.</p>'),
        ],
        note=""),
}
