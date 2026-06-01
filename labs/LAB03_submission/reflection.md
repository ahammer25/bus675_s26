

| Genre | Part A Accuracy | Part B Accuracy |
|---|---|---|
| Animation | | |
| Comedy | | |
| Documentary | | |
| Horror | | |
| Romance | | |
| Sci-Fi | | |
| **Overall** | | |

Then address these questions:

1. **Architecture choices**: Describe the image branch and tabular branch architectures you settled on. Why did you choose this structure? What did you try that didn't work as well?

For Part A, I used a custom multimodal neural network with two branches. The image branch used a small convolutional neural network with several convolution, batch normalization, ReLU, and max-pooling layers. This allowed the model to learn visual patterns from the movie posters, such as color, layout, faces, text style, and genre-specific imagery. After the convolutional layers, I used adaptive average pooling so that the image branch produced a fixed-size feature vector.

The tabular branch used both numeric and categorical metadata. The numeric features, such as runtime, vote average, vote count, release year, popularity, budget, and revenue, were standardized before being passed through a small fully connected network. The categorical list fields, including cast, directors, writers, and production companies, were encoded with embedding layers and then mean-pooled so each movie had one vector per metadata field. I kept the vocabulary size relatively small to reduce overfitting, because many actors, writers, and production companies appear only a few times in the training data.

The two branches were combined by concatenating the image feature vector and the tabular feature vector. A final fusion head then predicted one of the six genres. I chose this structure because it keeps the image and metadata inputs separate at first, then lets the model combine both sources of information near the end.

2. **Overfitting**: Did you observe a gap between training and validation accuracy? At what point did it appear? What strategies did you use to combat it (dropout, weight decay, early stopping, smaller vocabulary, reduced model size, learning rate scheduling)? Which were most effective?

I did observe some overfitting when the training accuracy improved faster than the validation accuracy. This started to appear after a few epochs, especially because the dataset is not extremely large and the categorical metadata can be easy for the model to memorize. The gap between training and validation accuracy suggested that the model was learning patterns specific to the training set rather than only general genre signals.

To reduce overfitting, I used dropout in the image branch, tabular branch, and fusion head. I also used weight decay through the AdamW optimizer, limited the categorical vocabulary to the top tokens, and used light image augmentation such as random horizontal flips and color jitter. The most useful strategies were dropout and keeping the vocabulary size small, because they directly reduced the model's ability to memorize rare cast or production-company tokens.

3. **Part A vs. Part B**: How did your custom CNN compare to the pretrained ResNet18? Did transfer learning help, and if so, in what way (higher accuracy, faster convergence, less overfitting)?

Part A used a custom CNN trained from scratch, while Part B replaced the image branch with a frozen pretrained ResNet18. The pretrained ResNet18 helped because it already had useful visual feature detectors from ImageNet, such as edges, textures, shapes, objects, and layout patterns. Since the movie poster dataset is not huge, using pretrained visual features made the model more stable and usually helped it learn faster.

Based on my results, Part B [performed better / performed about the same / performed worse] than Part A. If Part B had higher validation or test accuracy, this suggests that transfer learning helped the model generalize better. If the difference was small, it may be because the tabular metadata carried a large amount of the signal, so the image branch was only one part of the prediction.

4. **Tabular branch insights**: Which metadata features seemed most useful for genre prediction? Look at the per-class accuracy table — which genres did the model struggle with most? Does that make sense given the available features? If you tried ablations (tabular-only or image-only), what did you learn?

The most useful metadata features seemed to be the fields that directly connect to genre patterns, especially production companies, directors, writers, MPAA rating, and release-year-related information. For example, some studios or production companies may specialize in animation, horror, or documentaries. MPAA rating can also help because genres like horror and romance may have different rating patterns than animation.

Looking at the per-class accuracy table, the model struggled most with [fill in genre] and did best on [fill in genre]. This makes sense because some genres are visually and structurally more distinct than others. For example, animation and horror posters often have stronger visual signals, while comedy and romance can overlap because both may use similar poster layouts, bright colors, or character-focused imagery. Documentary can also be difficult because documentary posters vary widely depending on the subject.

5. **What would you do differently?** If you had more compute time or training data, what would you try next?

With more compute time, I would try fine-tuning the last block of ResNet18 instead of keeping the entire backbone frozen. That would allow the pretrained image features to adapt more specifically to movie posters. I would also test different vocabulary sizes for the categorical fields, compare mean pooling to max pooling for list embeddings, and run image-only and tabular-only ablations to see which input type contributes more.

With more training data, I would use a larger pretrained backbone and stronger regularization. I would also experiment with better handling of missing or zero budget and revenue values, since those zeros may represent unknown values rather than true values. Finally, I would look at the confusion matrix to understand which genres are most often confused with each other.


6. *(Optional — only if you completed optional extensions)* **Optional extensions**: For each optional experiment you ran, briefly describe what you tried, what result you got, and how it compared to your Part A baseline.