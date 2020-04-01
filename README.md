# Pandemic

## Generates animation of COVID-19 uptake against cases through time for specific countries and case thresholds.

A more optimistic view towards COVID-19

Exponential growth of a pandemic with time is hard to interpret as minor changes in gradients are smoothed out by the overall trend, making them hard to extrapolate and even harder to gain optimism from.

As the spread of disease doesn't depend on time, but instead on the current total confirmed cases and the transmission rate, we can ignore time when analysing pandemics. This has the effect of indicating when countries are beginning to deviate from unconstrained exponential growth and starting to "turn the tide" on the disease.

When countries begin to drop off the trajectory of exponential growth, it indicates the the country is winning the fight. It's reassuring to see that, although there's much more work to be done, the countries most heavily hit are beginning to peel off of this line.

The code I wrote to generate this plot is inspired by Henry Reich (from Minute Physics) and Aatish Bhatia.

Live data is accessed through API request URL provided by https://www.postman.com/.

## Installation:
Clone GitHub repository onto local machine.

## Prerequisites:
* Python3.5 or higher
* `ffmpeg` (image writer) must be installed to save animation:
    - iOS: `brew install ffmpeg` or `pip install ffmpeg`
    - Windows: `pip install ffmpeg`
    - Linux: `sudo apt-get ffmpeg` or `pip install ffmpeg`
    
## Acknowledgements:
* [Vagif Aliyev](https://github.com/vagifaliyev) for help in testing;
* Henry Reich (from Minute Physics);
* Aatish Bhatia, and;
* https://www.postman.com/ API host
