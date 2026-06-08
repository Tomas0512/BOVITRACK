"""
Seed: Departamentos y municipios principales de Colombia.
Uso: docker compose run --rm be python seed_departments.py
"""
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# (código_dane, nombre_departamento, [(código_mpio, nombre_municipio), ...])
COLOMBIA_DATA = [
    ("05", "Antioquia", [
        ("05001", "Medellín"), ("05088", "Bello"), ("05266", "Envigado"),
        ("05308", "Itagüí"), ("05615", "Rionegro"), ("05790", "Turbo"),
        ("05045", "Apartadó"), ("05197", "Caucasia"),
    ]),
    ("08", "Atlántico", [
        ("08001", "Barranquilla"), ("08078", "Baranoa"), ("08433", "Malambo"),
        ("08549", "Sabanalarga"), ("08573", "Soledad"),
    ]),
    ("11", "Bogotá D.C.", [
        ("11001", "Bogotá"),
    ]),
    ("13", "Bolívar", [
        ("13001", "Cartagena"), ("13140", "Carmen de Bolívar"),
        ("13430", "Magangué"), ("13836", "Turbaco"),
    ]),
    ("15", "Boyacá", [
        ("15001", "Tunja"), ("15176", "Chiquinquirá"), ("15272", "Duitama"),
        ("15693", "Sogamoso"), ("15759", "Soatá"),
    ]),
    ("17", "Caldas", [
        ("17001", "Manizales"), ("17380", "La Dorada"), ("17444", "Manzanares"),
        ("17541", "Riosucio"),
    ]),
    ("18", "Caquetá", [
        ("18001", "Florencia"), ("18094", "Belén de los Andaquíes"),
        ("18205", "Doncello"), ("18460", "Montañita"),
    ]),
    ("19", "Cauca", [
        ("19001", "Popayán"), ("19022", "Almaguer"), ("19318", "Guapi"),
        ("19698", "Santander de Quilichao"),
    ]),
    ("20", "Cesar", [
        ("20001", "Valledupar"), ("20011", "Aguachica"), ("20400", "La Jagua de Ibirico"),
        ("20621", "San Alberto"),
    ]),
    ("23", "Córdoba", [
        ("23001", "Montería"), ("23068", "Ayapel"), ("23162", "Cereté"),
        ("23417", "Lorica"), ("23466", "Montelíbano"),
    ]),
    ("25", "Cundinamarca", [
        ("25754", "Soacha"), ("25290", "Fusagasugá"), ("25175", "Chía"),
        ("25269", "Facatativá"), ("25899", "Zipaquirá"), ("25817", "Villeta"),
    ]),
    ("27", "Chocó", [
        ("27001", "Quibdó"), ("27006", "Acandí"), ("27361", "Istmina"),
        ("27495", "Nuquí"),
    ]),
    ("41", "Huila", [
        ("41001", "Neiva"), ("41132", "Campoalegre"), ("41298", "Garzón"),
        ("41503", "Pitalito"), ("41615", "Rivera"),
    ]),
    ("44", "La Guajira", [
        ("44001", "Riohacha"), ("44035", "Albania"), ("44078", "Barrancas"),
        ("44430", "Maicao"), ("44560", "Manaure"), ("44847", "Uribia"),
    ]),
    ("47", "Magdalena", [
        ("47001", "Santa Marta"), ("47030", "Aracataca"), ("47189", "Ciénaga"),
        ("47460", "Mompox"), ("47551", "Pivijay"),
    ]),
    ("50", "Meta", [
        ("50001", "Villavicencio"), ("50006", "Acacías"), ("50110", "Cabuyaro"),
        ("50325", "Granada"), ("50450", "Mapiripán"),
    ]),
    ("52", "Nariño", [
        ("52001", "Pasto"), ("52019", "Albán"), ("52215", "Cumbal"),
        ("52356", "Ipiales"), ("52835", "Tumaco"),
    ]),
    ("54", "Norte de Santander", [
        ("54001", "Cúcuta"), ("54003", "Ábrego"), ("54174", "Chinácota"),
        ("54418", "Los Patios"), ("54480", "Ocaña"),
    ]),
    ("63", "Quindío", [
        ("63001", "Armenia"), ("63111", "Calarcá"), ("63190", "Circasia"),
        ("63401", "La Tebaida"), ("63470", "Montenegro"),
    ]),
    ("66", "Risaralda", [
        ("66001", "Pereira"), ("66045", "Apía"), ("66170", "Dosquebradas"),
        ("66440", "Marsella"), ("66594", "Santa Rosa de Cabal"),
    ]),
    ("68", "Santander", [
        ("68001", "Bucaramanga"), ("68081", "Barrancabermeja"), ("68276", "Floridablanca"),
        ("68307", "Girón"), ("68432", "Málaga"), ("68615", "Piedecuesta"),
    ]),
    ("70", "Sucre", [
        ("70001", "Sincelejo"), ("70110", "Caimito"), ("70215", "Corozal"),
        ("70702", "San Marcos"), ("70742", "Santiago de Tolú"),
    ]),
    ("73", "Tolima", [
        ("73001", "Ibagué"), ("73024", "Alpujarra"), ("73148", "Chaparral"),
        ("73349", "Honda"), ("73411", "Líbano"), ("73800", "Villahermosa"),
    ]),
    ("76", "Valle del Cauca", [
        ("76001", "Cali"), ("76054", "Buga"), ("76109", "Buenaventura"),
        ("76111", "Guadalajara de Buga"), ("76520", "Palmira"), ("76834", "Tuluá"),
    ]),
    ("81", "Arauca", [
        ("81001", "Arauca"), ("81065", "Arauquita"), ("81220", "Cravo Norte"),
        ("81736", "Saravena"), ("81794", "Tame"),
    ]),
    ("85", "Casanare", [
        ("85001", "Yopal"), ("85010", "Aguazul"), ("85015", "Chámeza"),
        ("85315", "Paz de Ariporo"), ("85430", "Trinidad"),
    ]),
    ("86", "Putumayo", [
        ("86001", "Mocoa"), ("86219", "Colón"), ("86320", "La Hormiga"),
        ("86568", "Orito"), ("86755", "Sibundoy"), ("86865", "Valle del Guamuez"),
    ]),
    ("88", "San Andrés y Providencia", [
        ("88001", "San Andrés"), ("88564", "Providencia"),
    ]),
    ("91", "Amazonas", [
        ("91001", "Leticia"), ("91263", "El Encanto"), ("91540", "Puerto Nariño"),
    ]),
    ("94", "Guainía", [
        ("94001", "Inírida"),
    ]),
    ("95", "Guaviare", [
        ("95001", "San José del Guaviare"), ("95015", "Calamar"),
        ("95025", "El Retorno"), ("95200", "Miraflores"),
    ]),
    ("97", "Vaupés", [
        ("97001", "Mitú"), ("97161", "Carurú"), ("97511", "Pacoa"),
    ]),
    ("99", "Vichada", [
        ("99001", "Puerto Carreño"), ("99524", "La Primavera"),
        ("99624", "Santa Rosalía"),
    ]),
]


def seed():
    with Session(engine) as session:
        # Verificar si ya hay datos
        existing = session.execute(text("SELECT COUNT(*) FROM department")).scalar()
        if existing and existing > 0:
            print(f"Ya existen {existing} departamentos. Nada que hacer.")
            return

        dept_count = 0
        city_count = 0

        for dept_code, dept_name, cities in COLOMBIA_DATA:
            dept_id = uuid.uuid4()
            session.execute(
                text("INSERT INTO department (id, name, code) VALUES (:id, :name, :code)"),
                {"id": str(dept_id), "name": dept_name, "code": dept_code},
            )
            dept_count += 1

            for city_code, city_name in cities:
                session.execute(
                    text("INSERT INTO city (id, department_id, name, code) VALUES (:id, :dept_id, :name, :code)"),
                    {"id": str(uuid.uuid4()), "dept_id": str(dept_id), "name": city_name, "code": city_code},
                )
                city_count += 1

        session.commit()
        print(f"✓ Seed completado: {dept_count} departamentos, {city_count} municipios insertados.")


if __name__ == "__main__":
    seed()
