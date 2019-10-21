# StoneAgeAI with accompanying app in Kivy

This is a short introduction on how to interact with the code, there are two main ways:

- Train your own Stone Age AI using TrainingResultsAnalysis.ipynb, the training loop is there.
- Run StoneAgeGUI.py to play a simple app which allows you to play against a trained AI

The latter requires a pickle file with the format as shown in the second cell of TrainingResultsAnalysis.ipynb, an example is the file Q10.p
Basically, all the states need to be in the multi-index, with actions 0, 1, 2, 3 as columns depicting the values of those actions in the state in the multi-index.

Watch the accompanying video for an explanation of the game and two showcases of the app:
https://www.youtube.com/watch?v=GlZGcviUsOY

Packages used:
- Numpy
- Pandas
- Kivy
