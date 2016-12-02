./SentencesToGrammar.sh $1 grammar.txt
python grammar_viz.py
dot grammar.dot -Tpng > grammar.png
