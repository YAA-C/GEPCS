#!/usr/bin/env python
# coding: utf-8

# In[62]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# In[34]:


data = pd.read_csv("RUTURAJ.csv")


# In[35]:


data


# In[43]:


data.drop(['Z'], axis=1)


# In[66]:


x = data['X']
y = data['Y']


# In[78]:


plt.figure(figsize=(8, 8))
plt.plot(x, y)
plt.title('CS:GO Player Movement')
plt.xlabel('X Coordinates')
plt.ylabel('Y Coordinates')
# plt.ylim(0.01, 0.8)
# plt.xlim(0.01, 0.16)
plt.grid(True)
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:




