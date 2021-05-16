# Covid-19-Bot
Covid-19 Bot for FAQs

## How to run?

- Git clone this repo 
```sh
$ git clone https://github.com/ns3098/Covid-19-Bot
```
- Make Sure all dependencies are installed like Rasa, Tensorflow, requests, jsonpath and rasa-sdk
- Create a Virtual Conda env
```sh
$ conda create --name rasa
```
- Activate environment
```sh
$ conda activate rasa
```
- Assuming that all the dependencies are installed. Run
```sh
$ rasa shell
```
- And then in other terminal run
```sh
$ rasa run actions
```
- Now enjoy talking to Bot.

## Improvements
Due to the lack of stories and examples data, I couldn't add more features like finding CoVID-19 Testing Lab, hospitals and centers, Shelters and Free food. 
Actions for these features are added in actions.py file. Might complete later when time permits :).

<p align="center">
  <img src="/screenshots/Screenshot from 2021-05-17 00-00-02.png">
</p>
<p align="center">
  <img src="/screenshots/Screenshot from 2021-05-17 00-03-01.png">
</p>
