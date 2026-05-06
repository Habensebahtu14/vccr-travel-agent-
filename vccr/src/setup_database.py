import pandas as pd
import sqlite3
import os

# ── Paden ──────────────────────────────────────────────────────────────
CLEAN_DIR = '../data/clean/'
DB_PATH = '../data/agent.db'

# ── Relevante kolommen ─────────────────────────────────────────────────
TX_KOLOMMEN = [
    'Pers.nummer', 'Datum', 'Dag',
    'Van station', 'Naar station',
    'Prijs incl. BTW', 'Categorie', 'Productnaam',
    'Motief', 'Dienstverlener', 'Aantal Km',
    'Daluur-Reductie', 'Beschrijving reis',
    'groep'
]

BC_KOLOMMEN = [
    'Personeelsnummer', 'Status', 'Klasse', 'Abonnement',
    'Aanvullend trein-abonnement', 'Afdelingsnaam', 'Kostenplaats',
    'Begindatum', 'Vervaldatum kaart',
    'Fiets parkeren', 'P+R parkeren', 'Parkeren op straat',
    'Taxi', 'Internationaal reizen', 'BTM',
    'Deelauto', 'Deelscooter', 'Deelfiets',
    'Electrische deelfiets', 'Permissie deur-tot-deur dienst',
    'groep'
]

# ── Inladen en samenvoegen ─────────────────────────────────────────────
print("CSV's inladen...")

tx_a = pd.read_csv(CLEAN_DIR + 'tx_a.csv')
tx_b = pd.read_csv(CLEAN_DIR + 'tx_b.csv')
tx_c = pd.read_csv(CLEAN_DIR + 'tx_c.csv')

bc_a = pd.read_csv(CLEAN_DIR + 'bc_a.csv')
bc_b = pd.read_csv(CLEAN_DIR + 'bc_b.csv')
bc_c = pd.read_csv(CLEAN_DIR + 'bc_c.csv')

# Samenvoegen alle groepen
tx_all = pd.concat([tx_a, tx_b, tx_c], ignore_index=True)
bc_all = pd.concat([bc_a, bc_b, bc_c], ignore_index=True)

# Alleen relevante kolommen selecteren
# (filter op kolommen die daadwerkelijk bestaan)
tx_cols = [c for c in TX_KOLOMMEN if c in tx_all.columns]
bc_cols = [c for c in BC_KOLOMMEN if c in bc_all.columns]

tx_all = tx_all[tx_cols]
bc_all = bc_all[bc_cols]

# Datatypes goed zetten
tx_all['Pers.nummer'] = tx_all['Pers.nummer'].astype(str)
bc_all['Personeelsnummer'] = bc_all['Personeelsnummer'].astype(str)
tx_all['Datum'] = pd.to_datetime(tx_all['Datum'])

print(f"Transacties: {len(tx_all):,} rijen, {len(tx_cols)} kolommen")
print(f"Kaarten:     {len(bc_all):,} rijen, {len(bc_cols)} kolommen")

# ── SQLite database aanmaken ───────────────────────────────────────────
print(f"\nDatabase aanmaken: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)

tx_all.to_sql('transacties', conn, if_exists='replace', index=False)
bc_all.to_sql('kaarten', conn, if_exists='replace', index=False)

# ── Verificatie ────────────────────────────────────────────────────────
print("\n=== Verificatie ===")

# Check tabellen
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(f"Tabellen: {tables['name'].tolist()}")

# Check rijen
for table in tables['name']:
    count = pd.read_sql(f"SELECT COUNT(*) as n FROM {table}", conn)
    print(f"  {table}: {count['n'][0]:,} rijen")

# Test query
print("\n=== Test query ===")
test = pd.read_sql("""
    SELECT 
        groep,
        COUNT(*) as aantal_transacties,
        ROUND(AVG("Prijs incl. BTW"), 2) as gem_prijs
    FROM transacties
    GROUP BY groep
""", conn)
print(test.to_string(index=False))

conn.close()
print(f"\nDatabase opgeslagen: {DB_PATH}")
