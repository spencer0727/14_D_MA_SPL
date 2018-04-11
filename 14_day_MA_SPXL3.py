
from collections import deque
import numpy as np
import pandas as pd 



def initialize(context):
    
  
 
    context.window_length = 14
    
    context.highs = deque([0] * 2, 2)
    context.lows = deque([0] * 2, 2)
    context.closes = deque([0] * 2, 2)
    context.true_range_bucket = deque([0] * context.window_length, context.window_length)
    context.pDM_bucket = deque([0] * context.window_length, context.window_length)
    context.mDM_bucket = deque([0] * context.window_length, context.window_length)
    context.dx_bucket = deque([0] * context.window_length, context.window_length)
    
    context.av_true_range = 0
    context.av_pDM = 0
    context.av_mDM = 0
    context.di_diff = 0
    context.di_sum = 0
    context.dx = 0
    context.adx = 0
    context.pDI = 0
    context.mDI = 0
    pass


def handle_data(context, data):
   
    context.ticks += 1 
   
    context.highs.appendleft(data.current(context.ndx,'high'))
    context.lows.appendleft(data.current(context.ndx,'low'))
    context.closes.appendleft(data.current(context.ndx, 'close'))
    
    
    
    if context.closes[0] == 0:
        high_less_low = 0
        high_less_prec_close = 0
        low_less_prec_close = 0
        high_less_prec_high = 0
        prec_low_less_low = 0
        pDM_one = 0
        mDM_one = 0
    else:
        high_less_low = context.highs[0]-context.lows[0]
        high_less_prec_close = abs(context.highs[0]-context.closes[1])
        low_less_prec_close = abs(context.lows[0]-context.closes[1])
        high_less_prec_high = context.highs[0]-context.highs[1]
        prec_low_less_low = context.lows[1]-context.lows[0]
    
    
   
    if high_less_prec_high > prec_low_less_low:
        pDM_one = max(high_less_prec_high,0)
    else:
        pDM_one = 0

    
    if prec_low_less_low > high_less_prec_high:
        mDM_one = max(prec_low_less_low,0)
    else:
        mDM_one = 0
        
   
    context.pDM_bucket.appendleft(pDM_one)
    context.mDM_bucket.appendleft(mDM_one)
    
   
    true_range = max(high_less_low,high_less_prec_close,low_less_prec_close)
    context.true_range_bucket.appendleft(true_range)
    
    
    if context.ticks < (context.window_length + 1):
        context.av_true_range = 1
        context.av_pDM = 0
        context.av_mDM = 0
    elif context.ticks == (context.window_length + 1):
        context.av_true_range = sum(context.true_range_bucket)
        context.av_pDM = sum(context.pDM_bucket)
        context.av_mDM = sum(context.mDM_bucket)
    else:
        context.av_true_range = context.av_true_range - (context.av_true_range/context.window_length) + true_range 
        context.av_pDM = context.av_pDM - (context.av_pDM/14) + pDM_one
        context.av_mDM = context.av_mDM - (context.av_mDM/14) + mDM_one

    if context.ticks > context.window_length:    
        context.pDI = 100 * context.av_pDM / context.av_true_range
        context.mDI = 100 * context.av_mDM / context.av_true_range
        context.di_diff = abs(context.pDI - context.mDI)
        context.di_sum = context.pDI + context.mDI
        context.dx = 100 * context.di_diff / context.di_sum
        
    
   
    context.dx_bucket.appendleft(context.dx)
    
   
    if context.ticks == (context.window_length * 2):
        context.adx = sum(context.dx_bucket) / context.window_length
    elif context.ticks > (context.window_length * 2):
        context.adx = ((context.adx * (context.window_length - 1)) + context.dx) / context.window_length
    

   
    if (context.adx > 20) and (context.pDI > context.mDI):
        order(sid(37514),1)
        log.debug('buy')
    else (context.adx > 25) and (context.pDI < context.mDI):
        order(sid(37514),1)
        log.debug('sell')
