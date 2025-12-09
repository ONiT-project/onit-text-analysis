# ONiT Text Analysis
## Text Annotations
In the folder text_annotations_final/ we included the text annotations that were done in the [ONiT project](http://oeaw.onit.at/). The current upload includes 5750 annotations from 13 reference reports in German. The annotations were done on the available OCR data downloaded at the Austrian National Library.

## Retrieval Experiments with Marqo Vector Index
Interim results and code of the presentation given at the [DHd 2025 in Bielefeld](https://doi.org/10.5281/zenodo.14943196) are included in the data/ and src/ folders. We experimented with an LLM to improve the imperfect OCR of the digitized sources as a preprocessing step for vector index search. The repository includes the preliminary dataset and a code for visualizing the retrieval results.

# Funding Acknowledgement
The ONiT project was funded by the Austrian Science Fund (FWF: P 35245).

# References
```
@inproceedings{vignoli_voll_2025,
	address = {Bielefeld},
	title = {Voll automatisiert die {Natur} in historischen {Reiseberichten} erkennen? {Entzauberung} von {KI}-{Werkzeugen} und ihr {Nutzen} für die {Geisteswissenschaften}},
	abstract = {Der rasante Vormarsch Künstlicher Intelligenz (KI) macht auch vor den Geisteswissenschaften nicht halt. Die vielversprechende Hoffnung lautet, große, digitalisierte Daten-Korpora voll automatisiert zu analysieren und darin Strukturen und Beziehungen mithilfe komplexer statistischer Modellvorhersagen zu erkennen. Doch inwieweit trifft dies zu und können maschinelle Lernmodelle (ML) tatsächlich als unterstützende Werkzeuge für historisch-wissenschaftliche Argumentationsprozesse, auch bei nicht standardisierten, historischen Bildern und Texten, eingesetzt werden? Das Projekt „Ottoman Nature in Travelogues“ (ONiT) untersucht, welche Rolle die westlichen Darstellungen „osmanischer Natur“ in den zwischen 1501 und 1850 gedruckten Reiseberichten spielen. Dafür kommen KI-Werkzeuge zum Einsatz, die einen Distant Reading Zugang zur Beantwortung dieser Forschungsfrage ermöglichen. Unsere vorläufigen Ergebnisse zeigen, dass ML-Modelle eine erhebliche Hilfe zur Erstellung einer ersten Ordnung nach Relevanz von Bild- und Textquellen bieten. Sie zeigen aber auch, dass der Einsatz von KI immer im Bewusstsein der Möglichkeiten und Grenzen der Methodik erfolgen muss.},
	booktitle = {11. {Jahrestagung} des {Verbands} »{Digital} {Humanities} im deutschsprachigen {Raum}«: {Under} {Construction} ({DHd} 2025)},
	author = {Vignoli, Michela and Gruber, Doris},
	month = mar,
	year = {2025},
}
```
