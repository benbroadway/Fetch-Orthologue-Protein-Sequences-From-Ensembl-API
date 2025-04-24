import requests

ENSEMBL_REST_API = "https://rest.ensembl.org"

# Function to fetch orthologues using gene symbol
def get_orthologues(species="homo_sapiens", gene_symbol="MDC1"):
    url = f"{ENSEMBL_REST_API}/homology/symbol/{species}/{gene_symbol}?content-type=application/json&type=orthologues"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

    return response.json()

# Function to fetch species name and gene ID from Ensembl using a Protein ID
def get_species_info(ensembl_protein_id):
    url = f"{ENSEMBL_REST_API}/lookup/id/{ensembl_protein_id}?content-type=application/json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"⚠️ Warning: Could not fetch species for {ensembl_protein_id}")
        return ("Unknown Species", "Unknown Gene ID")

    data = response.json()
    species_name = data.get("species", "Unknown Species").replace("_", " ").title()
    gene_id = data.get("gene_id", "Unknown Gene ID")
    
    return (species_name, gene_id)

# Function to fetch protein sequences
def get_protein_sequence(ensembl_id):
    url = f"{ENSEMBL_REST_API}/sequence/id/{ensembl_id}?content-type=text/x-fasta;type=protein"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text.strip()
    else:
        return None

# Main function to fetch all orthologues and include species info
def fetch_all_orthologues():
    gene_symbol = "MDC1"
    orthologues = get_orthologues(gene_symbol=gene_symbol)

    fasta_records = []

    for entry in orthologues["data"][0]["homologies"]:
        protein_id = entry["target"]["id"]

        # Fetch species info (species name + gene ID)
        species_name, gene_id = get_species_info(protein_id)

        print(f"Fetching {species_name}: {protein_id}")

        # Fetch protein sequence
        fasta_seq = get_protein_sequence(protein_id)

        if fasta_seq:
            # Modify header to include species and gene info
            fasta_seq_lines = fasta_seq.split("\n")
            fasta_header = f">{protein_id} | Species: {species_name} | Gene ID: {gene_id}"
            fasta_records.append(fasta_header + "\n" + "\n".join(fasta_seq_lines[1:]))

    # Save sequences to a FASTA file
    if fasta_records:
        with open("MDC1_all_orthologues2.fasta", "w") as fasta_file:
            fasta_file.write("\n".join(fasta_records))
        print("✅ Saved all orthologue sequences to MDC1_all_orthologues.fasta")
    else:
        print("❌ No orthologue sequences found.")

# Run the script
if __name__ == "__main__":
    fetch_all_orthologues()
