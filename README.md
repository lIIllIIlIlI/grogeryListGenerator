The script will help you to generate your grocery list. 
There is a yaml file which requires you to input all you common meals with details.
The script will take some input parameters and generate a list of meals to cook,
a grocery list of ingrediences and a watchlist to keep an eye on your stocks, for 
example spices or rice.


Usage:
python grogeryListGenerator.py --days <number> --exercises <number>

--days: The number of days you want to cook for
--exercises: The number of times you want to exercise, this will increase you kcal needs



Planned features:

Lebensmittel exkludieren: Es sind nicht immer alle lebensmittel vorrätig oder gewollt. 
Möglicherweise habe ich keine Lust auf Lachs, es ist keiner im Supermarkt vorhanden oder
zu dieser Jahreszeit gibt es keinen. Es sollte eine mäglichkeit ausgearbeitet werden, 
Lebensmittel explizit auszuschließen oder einen impliziten ausschluss geben, zb anhand der 
Jahreszeit. Eventuell gibt es möglichkeiten den Prozess interaktiv zu gestalten.

Variation: Aktuell wird einfach zufällig etwas ausgewählt. In Zukunft wäre es wünschenswert,
vorherige entscheidungen abzuspeichern um eine größere Variation zu ermöglichen. Dabei muss 
natürlich noch geklärt werden, welche Suchläufe im Detail gepeichert werden.


