import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go
from Bio.Seq import Seq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

# Reverse complement function
def reverse_complement(sequence):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return ''.join(complement[base] for base in reversed(sequence))

# GC Content function
def gc_content(sequence):
    gc_count = sum(1 for base in sequence if base in 'GC')
    return (gc_count / len(sequence)) * 100

# GC Content Graph function using Matplotlib
def visualize_gc_content_graph(sequence):
    gc_percentage = gc_content(sequence)
    
    # Create a bar plot of GC content
    plt.bar(['GC Content'], [gc_percentage])
    plt.ylabel("Percentage")
    plt.title("GC Content Analysis")
    
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()  # Close the plot to free memory
    
    return img_base64

# Translate DNA sequence to protein
def translate_sequence(sequence):
    codon_table = {
        'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
        'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
        'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
        'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
        'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
        'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
        'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
        'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
        'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
        'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
        'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
        'TAC': 'Y', 'TAT': 'Y', 'TAA': '*', 'TAG': '*',
        'TGC': 'C', 'TGT': 'C', 'TGA': '*', 'TGG': 'W',
    }
    
    protein_sequence = ""
    for i in range(0, len(sequence), 3):
        codon = sequence[i:i+3]
        if codon in codon_table:
            protein_sequence += codon_table[codon]
    return protein_sequence

# Detect mutations between reference and user sequences
def detect_mutations(reference_sequence, user_sequence):
    if len(reference_sequence) != len(user_sequence):
        raise ValueError("Sequences must be of the same length for mutation detection.")

    mutations = []
    for i in range(len(reference_sequence)):
        if reference_sequence[i] != user_sequence[i]:
            mutations.append({
                "position": i,
                "reference_base": reference_sequence[i],
                "user_base": user_sequence[i],
                "mutation_type": "substitution"  # Expand to other mutation types if needed
            })
    return mutations

# Enhanced Mutation Classification
def classify_mutations(reference_sequence, user_sequence):
    if len(reference_sequence) != len(user_sequence):
        raise ValueError("Sequences must be of the same length for mutation classification.")

    mutations = []
    for i in range(0, len(reference_sequence), 3):
        ref_codon = reference_sequence[i:i + 3]
        user_codon = user_sequence[i:i + 3]
        if len(ref_codon) < 3 or len(user_codon) < 3:
            break

        if ref_codon != user_codon:
            ref_aa = str(Seq(ref_codon).translate())
            user_aa = str(Seq(user_codon).translate())

            mutation_type = (
                "nonsense" if user_aa == "*" else
                "missense" if ref_aa != user_aa else
                "silent"
            )

            mutations.append({
                "position": i,
                "ref_codon": ref_codon,
                "user_codon": user_codon,
                "ref_aa": ref_aa,
                "user_aa": user_aa,
                "type": mutation_type
            })

    return mutations

# Validate DNA sequence (Only A, T, C, G)
def validate_sequence(sequence):
    valid_bases = {'A', 'T', 'C', 'G'}
    return all(base in valid_bases for base in sequence)

# Generate PDF Report
def generate_pdf_report(results, filename="DNA_Analysis_Report.pdf"):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    file_path = temp_file.name

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, "DNA Analysis Report")
    c.setFont("Helvetica-Bold", 10)

    # Add analysis results
    y = 730
    for key, value in results.items():
        c.drawString(50, y, f"{key}:")
        if isinstance(value, list):
            for item in value:
                c.drawString(70, y - 15, str(item))
                y -= 15
        else:
            c.drawString(70, y - 15, str(value))
            y -= 15
        y -= 20

    c.save()
    return file_path

# Interactive GC Content Graph using Plotly
def interactive_gc_content_graph(sequence):
    gc_percentage = gc_content(sequence)

    # Create an interactive bar plot
    fig = go.Figure(data=[
        go.Bar(name="GC Content", x=["GC Content"], y=[gc_percentage])
    ])
    fig.update_layout(title="GC Content Analysis", yaxis_title="Percentage", xaxis_title="Category")

    # Convert the figure to JSON for frontend rendering
    return fig.to_json()
