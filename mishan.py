from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)

pytrends.trending_searches(pn='united_states') # trending searches in real time for United States
pytrends.trending_searches(pn='japan') # Japan