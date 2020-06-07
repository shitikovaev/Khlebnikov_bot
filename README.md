# Khlebnikov bot
The code of a telegram bot @hlebnikov_bot.

https://t.me/@hlebnikov_bot

https://teleg.run/hlebnikov_bot

Made as a course project for HSE University.
This bot generates a poem based on the poetry of famous Russian futurist Velemir Khlebnikov and lets you guess which of the poems is original and which is generated.
Technologies used - word2vec, pymorphy2, sqlite3, pyTelegramAPI, matplotlib

To generate poems, download ruwikiruscorpora_upos_skipgram_300_2_2019 model from https://rusvectores.org/ru/models/ , then extract it and put model.bin to resource directory.

To Host bot on GCP, use this tutorial: https://habr.com/ru/company/ods/blog/462141/

Also useful: https://habr.com/ru/post/326380/
