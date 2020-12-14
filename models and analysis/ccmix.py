from numpy import zeros, int8, log, random
import sys
import jieba
import re
import codecs

def ccmix(datasetFilePath, stopwordsFilePath):
    file = codecs.open(stopwordsFilePath, 'r', 'utf-8')
    stopwords = [line.strip() for line in file]
    file.close()

    file = codecs.open(datasetFilePath, 'r', 'utf-8')
    documents = [document.strip() for document in file]
    file.close()

    N = len(documents)

    wordCounts = [];
    word2id = {}
    id2word = {}
    currentId = 0;
    # generate the word2id and id2word maps and count the number of times of words showing up in documents
    for document in documents:
        segList = jieba.cut(document)
        wordCount = {}
        for word in segList:
            word = word.lower().strip()
            if len(word) > 1 and not re.search('[0-9]', word) and word not in stopwords:
                if word not in word2id.keys():
                    word2id[word] = currentId;
                    id2word[currentId] = word;
                    currentId += 1;
                if word in wordCount:
                    wordCount[word] += 1
                else:
                    wordCount[word] = 1
        wordCounts.append(wordCount);

    M = len(word2id)

    X = zeros([N, M], int8)
    for word in word2id.keys():
        j = word2id[word]
        for i in range(0, N):
            if word in wordCounts[i]:
                X[i, j] = wordCounts[i][word];

    return N, M, word2id, id2word, X



def EStep():
    for i in range(0, N):
        for j in range(0, M):
            denominator = 0;
            for k in range(0, K):
                p[i, j, k] = theta[k, j] * lamdab[i, k] * (1-lamdac[i,k])
                denominator += p[i, j, k];
            if denominator == 0:
                for k in range(0, K):
                    p[i, j, k] = 0;
            else:
                for k in range(0, K):
                    p[i, j, k] /= denominator;


def MStep():
    # update theta
    for k in range(0, K):
        denominator = 0
        for j in range(0, M):
            theta[k, j] = 0
            for i in range(0, N):
                theta[k, j] += X[i, j] * p[i, j, k]
            denominator += theta[k, j]
        if denominator == 0:
            for j in range(0, M):
                theta[k, j] = 1.0 / M
        else:
            for j in range(0, M):
                theta[k, j] /= denominator

    # update lamda
    for i in range(0, N):
        for k in range(0, K):
            lamdab[i, k] = 0
            lamdac[i, k] = 0
            denominator = 0
            for j in range(0, M):
                lamdab[i, k] += X[i, j] * p[i, j, k]
                lamdac[i, k] += X[i, j] * (1-p[i, j, k])
                denominator += X[i, j];
            if denominator == 0:
                lamdab[i, k] = 1.0 / K
                lamdac[i, k] = 1.0 / K
            else:
                lamdab[i, k] /= denominator
                lamdac[i, k] /= denominator


# calculate the log likelihood
def LogLikelihood():
    loglikelihood = 0
    for i in range(0, N):
        for j in range(0, M):
            tmp = 0
            for k in range(0, K):
                tmp += theta[k, j] * lamdab[i, k]*(1 - lamdac[i, k])
            if tmp > 0:
                loglikelihood += X[i, j] * log(tmp)
    return loglikelihood

def output():
    file = codecs.open(topicWordDist, 'w', 'utf-8')
    for i in range(0, K):
        tmp = ''
        for j in range(0, M):
            tmp += str(theta[i, j]) + ' '
        file.write(tmp + '\n')
    file.close()

    file = codecs.open(topicWords, 'w', 'utf-8')
    for i in range(0, K):
        topicword = []
        ids = theta[i, :].argsort()
        for j in ids:
            topicword.insert(0, id2word[j])
        tmp = ''
        for word in topicword[0:min(topicWordsNum, len(topicword))]:
            tmp += word + ' '
        file.write(tmp + '\n')
    file.close()


datasetFilePath = 'combine_dataset.txt'
stopwordsFilePath = 'stopwords.dic'  ##停止语句
K = 5  # number of topic !!!
maxIteration = 30
threshold = 10.0
topicWordsNum = 8
topicWordDist = 'ccmix_mix_distribution.txt'
topicWords = 'ccmix_mix.txt'

N, M, word2id, id2word, X = ccmix(datasetFilePath, stopwordsFilePath)

lamdab = random.rand(N, K)/5+0.8
lamdac = random.rand(N, K)/4

theta = random.rand(K, M)

p = zeros([N, M, K])


# EM algorithm
oldLoglikelihood = 1
newLoglikelihood = 1
for i in range(0, maxIteration):
    EStep()
    MStep()
    newLoglikelihood = LogLikelihood()
    print(i + 1, " iteration  ", str(newLoglikelihood))
    if (oldLoglikelihood != 1 and newLoglikelihood - oldLoglikelihood < threshold):
        break
    oldLoglikelihood = newLoglikelihood

output()