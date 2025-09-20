Test Website can be accessed on 
<a href="https://pyblockchain.onrender.com" target="_blank">Render</a><br>
<small>It may take 3-4 minutes to power the project on</small>

The whole notion of PyBlockchain is test implementation blockchain written with Python.<br>
To make the system faster and enviroment friendly no mining mechanism is implemented <br>
only on cpu 1K-2K TPS <br>
and on gpu 10L-30K TPS <br>
it may increase with a little of tweaking and improvement like ~100K on gpu.

## Config
- Pooling is set to 5 tx per block,Tx will hang in there til pooling gets fulled. <br>
- Config_Fee is a multiplier of tx amount, and not a constant (which may cause DOS attack)<br>
- Config_Tax is a multiplier of tx amount, is used for airdrops and  funding stake <br>
- Total_Supply is total amount of coin on system, it is just for refrence (is not used) <br>