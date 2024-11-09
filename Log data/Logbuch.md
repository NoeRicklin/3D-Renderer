# Logbuch

* 2024-04-19: Erstellen des Repositories und grundlegendes Aufsetzen der Python-Datei.
* 2024-04-21: 2D Projektion von Punkten auf eine Kamera erstellt, um die grundsätziche Funktionsweise in 2D zu testen.
* 2024-04-22: 3D Projektion eines Würfelsgitters und mit tastatur beweg- und drehbare Kamera
* 2024-04-23: Funktionalität für verschiedene Farben eingeführt
* 2024-04-24: Möglichkeit die Kamera rauf und runter zu schwenken und mit der Maus zu bedienen eingeführt.
* 2024-04-25: Objekt- und Kameraklassen eingeführt um mehrere Instanzen davon nutzen zu können, wenn benötigt. 
Da jetzt auch viele Objekt- oder Kamera bezogene Funktionen in die Klassen gesteckt
werden konnten ist der Code jetzt etwas übersichtlicher.
* 2024-04-26: Dreiecke werden jetzt von zuhinterst bis zuvorderst gerendert, um die richtigen Dreiecke schlussendlich zu 
zeigen. Dieser Weg geht allerdings nur, wenn sich keine Dreiecke überlappen, was aber eigentlich hier gegeben ist. 
Dreiecke sind jetzt auch eigene Klassen
* 2024-04-27: Funktion kreiert, die aus .obj Dateien die Daten der Punkte und Kanten extrahieren und sie für den
Renderer lesbar speichern kann. Auch werden jetzt die einzelnen Dreiecke je nach Winkel zur Lichtquelle gefärbt, um 
Schatten zu simulieren.
* 2024-04-28: Funktion kreiert, die ein Objekt beliebig rotieren kann.
* 2024-05-15: Kleine Optimierung eingeführt, die für jedes Dreick erkennt, ob dessen Vorderseite zur Kamera zeigt. 
Ansonsten wird damit nicht weitergearbeitet, weil es nicht sichtbar ist.
* 2024-07-01 - 2024-07-05: *beschrieben in "Log data/Arbeitstagebuch Spezialwoche.md"*
* 2024-09-15: Schreiben der Einleitung der Arbeit
* 2024-09-19: Erstellen der Raytracer Datei und der Funktion, die die Farben der Rays auf den Bildschirm zeichnen kann, 
wenn sie berechnet wurden.
* 2024-09-21: Funktion kreiert, die für jedes Pixel einen Ray an der richtigen Position und der richtigen Richtung 
kreiert und in einem eigenen Objekt speichert
* 2024-09-24: Funktion kreiert, die für ein Objekt die Dimensionen der Boundingbox parallel zu den Achsen berechnet
* 2024-10-07: Funktionen kreiert, die berechnen, ob ein Ray erst mit der Boundingbox eines Objektes kollidiert und dann,
ob der Ray mit dem Objekt selber kollidiert
* 2024-10-11: Funktionen implementiert, die die Beleuchtung der Kollisionsstelle eines Dreiecks mit einem Ray berechnet.
Auch wurde die Skybox aus dem Rasterizer in den Raytracer übernommen.
* 2024-10-12: Worddokument der Arbeit formatiert und mit dem Schreiben des Rasterizer Kapitels angefangen
* 2024-10-13 - 2024-10-19: Fertigstellen des Rasterizer Kapitels
* 2024-10-20: Schreiben der Einleitung für den Raytracer
* 2024-10-25: Beginnen mit dem Schreiben der Implementation des Raytracers
* 2024-10-27: Fertigstellen des Kapitels über die Implementation des Raytracers
* 2024-11-03: Schreiben des Kapitels "Vorgehen und Methoden", der Übersicht in der Einleitung und Beginnen mit dem 
Kapitel "Vergleiche und Resultate"
* 2024-11-09: Fertigstellen des Kapitels "Vergleiche und Resultate"