from django.db import models

class DNAAnalysis(models.Model):
    sequence = models.TextField()
    gc_content = models.FloatField()
    translated_sequence = models.TextField()
    mutations = models.TextField()  # For storing mutations in JSON format
    created_at = models.DateTimeField(auto_now_add=True)

    def save_analysis(self, sequence, gc_content, translated_sequence, mutations):
        self.sequence = sequence
        self.gc_content = gc_content
        self.translated_sequence = translated_sequence
        self.mutations = mutations
        self.save()
    
    def __str__(self):
        return f"DNA Analysis #{self.id}"
