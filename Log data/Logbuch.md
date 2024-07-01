# Logbuch

* 2024-04-19: Erstellen des Repositories und grundlegendes Aufsetzen der Python-Datei.
* 2024-04-21: 2D Projektion von Punkten auf eine Kamera erstellt, um die grundsätziche Funktionsweise in 2D zu testen.
* 2024-04-22: 3D Projektion eines Würfelsgitters und mit tastatur beweg- und drehbare Kamera
* 2024-04-24: Möglichkeit die Kamera rauf und runter zu schwenken und mit der Maus zu bedienen eingeführt.
* 2024-04-25: Objekt- und Kameraklassen eingeführt um mehrere Instanzen davon nutzen zu können wenn benötigt. 
Da jetzt auch viele Objekt- oder Kamera bezogene Funktionen in die Klassen gesteckt
werden konnten ist der Code jetzt etwas übersichtlicher.
* 2024-04-26: Dreiecke werden jetzt von zuhinterst bis zuvorderst gerendert um die richtigen Dreiecke schlussendlich zu 
zeigen. Dieser Weg geht allerdings nur, wenn sich keine Dreiecke überlappen, was aber eigentlich hier gegeben ist. 
Dreiecke sind jetzt auch eigene Klassen