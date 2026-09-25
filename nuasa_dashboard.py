"""
NUASA Financial Dashboard
==========================
A Streamlit dashboard for the NUASA (PAU Chapter) financial records.

Main dataset : NUASA's First Bank statement (the official account).
Supporting   : Informal transactions made on behalf of NUASA that did
               NOT pass through the NUASA First Bank account.

Uses pandas only (no database connector) - both datasets are read
straight from their CSV files.
"""

import base64
import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="NUASA Financial Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# CONSTANTS
# --------------------------------------------------------------------------
MAIN_STATEMENT_FILE = "NUASA_s_first_bank_statement.csv"
INFORMAL_FILE = "Informal_transactions_on_behalf_of_NUASA.csv"

LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAIAAABt+uBvAAAQAElEQVR4Aey7d5yeRbk3PjN3f9o+W7M9u8luCmmkURIIEHpRIBQRlaNHKaKCgHAUpYhB9BzLeRERLMcuRZQmIaFDKum97W6yJVuy7enP3Wd+3/vZJAQFyb5H/vm9zOe788zMPeWa71xzzTX3nbCnn376mUJ49tlnn3vuuecPhxcKYcmSJS+++OLSpUuXLVv20ksvvXw4vPLKK6+++uprhfB6IbxRCG+++eZbb721fPnylStXriqE1SvXrlm1Dnh79fq1a9ate3v92rXr163bsH4kbNywYdPGjZs3bd66ZfPWTZu2b968Y8umHVu27Ni+decOYNuundt37wJ272kZwZ69rS1797e2tANtbfv37Wvft2/f/v3729vbOwqhsxAOHDjQXQg9PT29vb19hXDwcOjv7x8cHBwaGhoeHk4UQrIQUoWQTqczmUy2EBj50AMn5AiIoEhjyJEYiXeBiSBLgyj4g3BHQNCQcjwCRtJBHNR6766CJ/+KPwjwr+jm/fsAI/8E724HYRgTBRCCDBWkAE7F++LdPfzrcxDjX9/pu3vkIAhKhBgoPPpna15gZISXQl1C6FEglB+Nwx2SDy986AQJSrAxEB81Bwx6CIfpYFS8JwgqEMEAQbD/ACLIOziqzw8rCUE/rK7Rb4GXYAhOGGgiwb4Jsnh0jCj0QI6KGdKCHolH19sxDnp0tQ99gGCwEbNSUAToAhX/qCyBplARxIX5k8MxCxQHdJAgwQ/HSBxGUDMY4kP7+3AJwpxJgZ1AfnH0WDwoIUdiJN4DgYmhXKAqTA9iQjjFT9CPoEFMApVEyYeIkWE+xAEE97jvEuHDFkFzEHPPdR3Ld52gkApJpoqE6XKCB54thA8eRgDbQwUnwkchkwiqqTJjhHPPQXOJCg1FAX9EHA6YCZKI/1X40AnCbCSJqqosyyNjcU1XYrEYYkmSCOWeh+k6PvEJKMCEmUAhgI1FKUUdNFQk2bUtwHNs4XvgU2WUCs49919FxPv1MyL0+z3935dzRWZQIsc2PdfGnKAvnPiWY5qW5XoeoVRWFFnRCJU8X1i2KwoeD/eJ53Lf81zHGYGmygrUhwqoocQIYigjOaRu/3s537eHD5ugYGAoj6ZpYAHK7zq+7XiuRxRNZ5LmCmZ5AvCIRGRD1sNcKFxIiAWRCTafrMuKoah63nQ5J6qqG6ohQcFcz7VshGCAD/PvwyaIQS9cj4MUz+MCplXSJMUAfKJwplI5LKlRSY9TNUbkCJfCHjW4HJHUmKIXK0ZcNeKKHlW1SCRaLIiczpjpbJ4TpocjRiSqaQYhH+4UPtzesbSqqmMOvk99ziRZV7SQrIQEMw50D23d0frCC68+9PCvv/HNxV/6ytevveGWL1x3yxdvuuO6G7927Rdvvfm2b97/nw/+/rG/rli9cXdLp080PRwvKa0wIkWOK8AU1FANCMIgHyLYqPseXQOGfeT5zHUpqNGM2OBQ5oUlr33ve//99Tu/fd/9P3j40d/95Zllb63cvGV7W0vbwfbO4T1tfbtaerbs2v/Wmq1PPr30xw/98rav3/3562+64Uu3PvTorzft2OsJWY/EqKxZLs/ZHtgfnUSjrP2/JYgKEiBwUHjhbD40vgicOlkIxXOleHFNpKgCFCx+4EfX3vjV7//ooVfeXDmYzKUztuNyBupUI2TEQqGIbkSgJoBsRGW1oGuSIpjOmbZlx55HH/3tddd/9bav37v01eWmx7RokU8kj0o+lbH7MOLI2DDeR3BEJDwdwUidY4//LwhCE3ZIAowZrCBnxFck4nu2aeYURQlHI5brWY4oilfLcsnat3ff/92H7vzmAy+8vNLkaqi4XIkWyZGoGglNmDxp8uSJl37sggXz5p6+4KSpUyecd/45N9z4xVNPPfX8C85duPD0iRMnhsMRBXtTicpa3BOhlau3fuWWb93wldteXr7CFKSsqjZnU44KWohQCYLJlIR0hREXUiFLCIeYnIBHBTHSx84OajL8jR5w3oKGwR8JNIgQ4vsuXJuS0rjj2YPDaV2PSZKxY0/bj37ys//84YOvvr7C8rhmRAiVCVMw5/nz58+ZM6epaXx1zZh4cVFpWbyqsryhvkZXFFmisXDYMIx4cWzSpIlnnXXm1Z/5VF1DnR7WI0WxnGXHSspyFrnn3h/c8fVvL1m2PBIvzZsejjnfF3nTppSauSz0GtQQIiDbIQiGQ+JQ+ph/RuZ4zNUxIPVwAwhGEvJIs0JaIjhNBKOUyLIsyZrrs41bd/7gRw8ueeWl9v4DRWXxMWPGZJKpsVVVX77uugvOOlsl8AS5ZeeHkkMtbXu3bNu8ctXyt956Y+mS55Y9/7f1b6/ZsnHDvtbWfC5jhJSa2vLpxzdf9emLK6oi0bgmhNjX1p1PS68sW3//4v966KGHDT3MFJXJWnFJWSZvWo4bSAWRCB0REstIiUcFP5Q95p/REvTOAIIwHkhAiAgSnEiKpvUPDCazpqJGnn52yT33fLets1OFKoT1yprKCz9+YVPTuHQqWRKLeZbZ39Pd1b5/84b1b69e+epry9auW7N9++bOjrbO1p17tq3rat/Ttnfb9m3rV69886mnnvzFL36BV6qqosHtrq+vv+6660477TToSzQc6+jq+fkv/ufOb92VzVlwKQ4ODBuhSLSohIMaEbCDP0o4vFUGQYmP7DGTE1QcLUFBG06huIcacgL7jIgwSekfSGjheDhS9sP//umDP3mkqLQcK4mdsmjRpTU11YT6Z567EC7RA99f/Njjv3/jzVf27NiaSQxWlZVNP27SeWctvPiSiz519aLPf+7Kj10w/4wFM6ZNqa+rLtZUmhhM7Njesn7trqf/8tLO7R0zpp3gWLYs+Tff/Pm6sWW6rsWi8WefX3Ljl24GWZFoMbTHsnEFYZAzEJdAPCQBjxbShcJjjQ7N8xirC1qoLxBzLM8ICA3SjuvHi8dQFrlv8Q9ffm3l2KaJQ6n0rDmzFyw4dVzj2Nq66h1bt7z04pKBwYOWmVEU6dyzF179qU/ccutN//Vf93//e4u/+527b7/5KzfdcO3Xb/vyPd+67acPfv93//PIr37+8H33fuvaz11z9plnKJT1dvcXRUv+9twLGzZsKC+N79yxYcGpcxsa630hjams3r5z11dvub2lrb2ouAwc4VwjgYJDVAIJCfUCBASRUYVC+1G1CEzPSCvw8g60UDidcb5553c3btwrq2GY0osvX1RSVlIcj617G182VuzcsaVzX0tIlU+bf/Lie+++5dav/Pvnrzlj4anjmxtVhfhOzs0mvVwmlx5OJgaS4DGXikf1eSfOvuNrX3n4Jz949OEfX33lpcVF0cTQwOqVK1Ysf9PMZ3zfmTBhwuTJx8EdjUaL97bs+9KXv7py1dqqmnpBGDgShGAVqSAUXjwQEMRHNd2RqR5zk0B30IQRygME7ZhPGSfy0FDmZz//zb79PcmUCSswY9ZM27bHNja+8trLW7dubmvZi1v4WQtPu+OrN13/75+bN3cmcezAK8gmzVwinxnmjiVzP6QxQ2fRqBYrCocMRfhuPpP07DS3U7NnTvr2Pbc++tAPPvvpq8aUxg907Gvds3twYCCdyp5zzjlTpx8/nEhV1tTmTOvue7+zbv1mTiRR4IgEMgeCEshMRCE1ioiNom6hqqbh6kA8zj3h5S2LybLtcD0cf+ZvS994c1UilalvbJg9e3ZJSQmldMnSF4eTQ53dHdGw/pmrP3H7TV8+edZMxfes5HBEkSTHVH2HWfmySCikEEODibAJtV0v79g533UViRWFdZlyidjUS5uZvkkTxnz/e3f+1/fvnT7tuN7unjdeeR0TGBwcxHBXXXWVpocElbt6Dn7znm8nMnkjWuRyoRmhXN6CMMTnQVyYxbFH6P/YK+NgIJZlooGiKIyxcDicN91YUfnfXnjl2WdfrK1v0EMgUDrxxLmN9XXd3d39fQf7hw6eetopX7vtlrPPON3EoZ1NyRrD7hBmtkxRyzkNp/Mxz4/I1BVWxs/5BF6EDx9PYo7MTEaywktxJ8W9rMJ8x8ykhg9edMFZv/jFT6+44mLXz69ZswL7rbS0tKS8rKqqJpPNV9eOXbXy7Ud//qtEKqfp4ZzpRqNFqqp5nHDOIfyoMDqCCOGea8uUgB2ori+4Hg63tvbgzmmES7t7++bMnfHVW764bt3K9evW4tNnSFXOPOO0Ky6/dO7MGTLhMJOyzlz4tCqpiEXYwHBqw87+lRsHN223BwZclVsacTwqM1XTBKHJfL4tndrrOj2qbIVUVThE4lpprCyXzY1rqL773ttuuunzpplq2bNr7+6de3bumjV3zimnLOjpPVhWWfPkX55b+tLrihZ2PXQl+ZwQQhmTyCjDaAkikkRlSeIu932RtzxJDj3552e6ugccl6u6Xl1XLStkfGPdutUrPMua1DT+C5/7bHVFeWKgP5tJ2a7lM18KSQxuIvd6WlqGd7eIA73ZfZ32wQFV4oxRCe9ghUR53jb706n2bG6/4x2kNG/lk6qqSoQlhtPC83PZlKGxb3z91k9ffSWj/soVb+E78uRJU2bPPdEIF6laGBv157/8ddeBXj0Uy5kONJ1J0HtllPwQNtoGEmXC93wojy+pSnjtuo2r1m6A3+r43qWXLtI07S9PPvnKS8sMhU0cX3v9Fz4TliXq2RLxYxEDE8yaWUBS5XRy2MlnFNfVPc+wbM20IpYb9TmzXG5ZvpkVblKIBOeDrjdguQeZ7OTyyHJNM7hPKZV0VfNd+//86L7LLrk4l8u0tbUsXbZk06ZNV199tYy1CsW2bt3256eekRVdUUPYW4qiuR4UaXRTHl1tKohEheviHsggouezJ596RjDKZNrU3JxIJadMmdHV1dO+ry1kqJdefF5IoUP9vZosK6rs+66myprEhGfLRMSKI/VNjeHKIl+j5WXFtZFYPGVGBxOp7h2O1W1objSEu4PEPUKEpMgapaK8ogR2ShAnHNGJD6fay2azlkUWf+feU04+KWRoL/7thaKiovbOzinTptmWGysp+9Pjf27Z2xYOR2GqKVNt2x2tQoyOIPQuYY8JIcsyo/LGDVv37mnTdbW0vHjuSbNDodBvf/On4YFMaXHpoosvnDp5nBBmaXHMtizLtl3uW9lciLJKLcyzucHkECuLVJ40ZeJZJ4+fNTlMSXLFltZnnuWpLZazRfABRZJDSlVEGx/WGnStKhQpTqWGNMOTlDxhOSMkOZalylpiaCAeJ/d/d/HAwMHS0uLdu3dbljV7zpxIDCHe09P32BNPDidTqqo7jkuohCmMCqMjCE6XLMtMlomscCa/8eYKIxTL5nPVVWNSiWHuecmBgVwqOXvGtIVnLPBdR3guEUKCzRpRA8Mwc1ZqMBmR1Lisa76n+25+oGfTG6+veObZ/g1b1OHBkrDtOR2Jge1OrqM0TutrSoriMeyMnO04wnd9W9GlTD6TSGeK42V4Px2JRLJZjDNuKQAAEABJREFUb+b0uv984L7U8MHkcH9dTU37/v0NDQ3ZTL6sfMwzz73Q3tHtEQlOiaZpo2IHlUdHEBr4lJm+IEq4rbNv3aatgkqqZFRX1pSXVry96q1Mqqe+Nnbl5ec5ZhJnqi+YJiue58FCoSHe2xBdM6LFfR19W5e+ufmxp9c+9MuOJ5/OrFkbGR4mZrq2tryutkqiec/cY6fWHOx8fnDg9bS1tzvZOpAd5JIqmGE6lCqh4rLqbMZlQiXcp9yG7f3MlR87+/STejtbn3rijy8tWdLV0YG1NF3/4GB6xdubojEZUkO5MIVRYdQEDQwN6kZIVoxtu/b6Al6dW1FRMba+MZtOu66tMO/4aRMUWZDAl+SU0pxlSpLEJNl0fEdIQgsxLVRRO/akBafFi8sNVSsLx2r0SJQw7npaOESDukKT8gpLEZpK5vr39Xa2dHf3DmfQVgpF+zP5bfu7dnZ0+ZKcd2xZkSj389mkpojzzzkjFlY926qoKKuvrS0pK3VsT1LVVWvWt3flZFVVDX1U7KDyqAnCzsY6HDhwYPPmzeFwGBRMmTLlhBNO6OvryeVyeHrSSSdh6YQQvu/jkLQcUzYUPRTxiZSySNaVUjb3ozGnbsy4i88vPm1Bj27kuCSokuK+XlHhSDK+BUlMYVLIo3E50mjJtbs6ze5hi2uRzmT65XXrXt60ednGtfuGullY5kIoigKRIMnHPvaxSZMmOY4DMeBYn3zyyZIkQZg1a9bs2rUrEokEImHSo8GoCYIc2MmJRAJDZrNZCAeB/vrXv/b19eXzeez8cePGQQ5UwxajhITDmkSEmcu0tLQuffXNv770xl9efuvplev/trOtr7g8Pn+BMWPWgCQNu55WXKLGorbnS7Jm+VrWDbPYBKl0SoJU7E+yHV2Dg47fb+Y7BgZNSrsGhna2tXDsLt+GZgAYdMyY0nPOOQfjmqa5ZcsWCAnxsIrIQlrD0LFsoyEnqPt/QxCWBRrkum4oFK6ursY9CGn4aehv8uTJeArKQBCyhHAOLbdyBqPhkDaYy+7q7V/R0vXshj3Pbun88Qtw73K1Z59bOndO0lBIJMRkhXiuTHVHFPNwEymduXsosrIldVBE+ly6u7fPk5RQrAjOZETRQqqmK6pEKKjRdX1kRBCE9evv78fGP+6446ZPnw4NMgwD/lE+b0KwglSjiEZNUDqdxrL09PRgoWB9MTYhFOlMJgMfpKmpCRsNWYgLYMVQWZYkzKSmqrq6tqasujpUVU9LatoS7tp9g795bc3KvuExC8/UJk9uHRqQdUNTw+kUZ5HxRfXze7LFa3YOHhhyiFHk66Fd+9u1cPikOXPry8pnN086cfpMiUiqokNBCCEgwrZ9vMOur69PJpNgBGuGlYOoWLPOzk5UK0iLuqMAG0XdQlVNNfr7B1tb2qKRIhABVVq7du2yZcuwOFVVVaWlpUjIMmMSagdG2jRhcpjl+JFYUWVFOZY6a5tD6TyhhhEd09qf+/my5SuyvjLrRDsSy7k+XhAo4RoWn9aZiq/eNtDRa6pqSJGkrGnta+9MDiTmTx5/8fx5Zx0/s6GsIjuYkBjDOgEQhjEWCpG5c+dCBtABppqbm6HgeAo5OwrnGsQaFUZNENQEqgF9gaZg55977rmf/exnZ82aBT0HOyjB8CMxqgGaETbCIdu2hc+LjHBEVRVZC0VjqhJKZuyiyrEtw7nfLV+dr65vmn9qZyJ3YNiva57nqPUvr2jbvqOXW4zmTCmXCVGa7O9/belL7W19JYqqC89Kp2SJCs8FL1BVDKEoMHpk2rRpEAYqAyFhJSEDsrIs5/N5pCHeqPC+BKEv4Oi+IASAlfFcPjAwALFCoRA2PIRIJBIgJR6Po1BRZNsxPc9DWyZLHhUpfIRhRJelqKJGJD2byhLKCAs2ZjZvh4vHdGTMl7ZsK5s63YqVKVVTWwbkJ55d1ddvN9dPmNnYdGLj2FOaG09orF8wfVqxpq1esbzvQJfMuMtNwVzYaUVRIBh0M593fJ+MHTsW6Wg0Ojw8jERlZWVxcTE2HWQGTagJwQAkjgDZ98P7EvR+DcLhKOgAEVAl23Z37tiN8wtLhME0TaEU7zYFnhIiYJpQCG2HlBFDz2fSRbF4NmdyyoJCmWoSC2t6NBLJ2s4OvHB33KoZc3NK+f4+59TTLvr4hZdfccnFF51z1scXnv7x004596TZl599+icvueiMeScXxaM50/Q5zi+GITDoCJCWJILhJEnasWMHslhCGE1QAwlRrijK+83r/cpHTRA0CLuaEIaBOeennHIKDguoNySANBgGhQWCCGJsK7BgpdNEuIFwRujA8LASNiSZObmMsNJueshJD0meZTvWgO1klFhZ3dS6+ulVY2plQto7Og8c6MT3soHeAyXMj1OnPCIXF4eIjDcjBOpAhE+Fj4EwLjgCI0jgXAdBMIjQYkgF9YlEIlgSYKQm6hw7RktQUN+2sXQqpQwyLV++HOcFEuAFuwwDI/GOHNzjtqvIOMcUX1b39/QNJlPYHNRKxag9qark5GkTrrjgnDtvu/mL111bNKZqxbrND/30V889t+SB+xYvvu/b3/3eA/d8577Hn3wqMTQoHNNJDntmmvo2IYLJqgRNzNl4E4/RR0YcIUhVIVtw9re3t7e2tmJzoXxEfWANIOGoEEx4VA1QmTEZu2xELLiFMD1YTAhxNFCNEI5YZZKmGnlPtpm2fU9LNpeMCHNOQ/nlp8+98aqLPnfZ+ZMbqjp3b//zn37/u9/94cUXXzTTybBMTz35hC/eeP2iKy/TIqH5+HDU1EwFUxUlFglHwnCqBPF8WSgy06jAIATCYHTEyOBoxyLB9EC1GxsboVAQDyXwtlEHFUaFURMEIbC5YrEYNhQ0GdsbiwMdxtjYfZz7GB7SIAswRlRVdhzPFtLAULpj3/7pTU2LzjrjotNPOXXOtP6O1j88+pMnfv1I5+5tY8tLF1144e0333zTDf++6OLzLrjw/BNOmDHQ3w9GFpx8kk5VO+c6FnUdvAjChychM8okmam6IKwwEMNugmwYHSoDjmAZscVgp7u6upCFkHg0omhIHDtGTRAOSzipuh7CgoCIefPmTZ06dWQ8KHBBSuHhLQfBJUlAYtOxJCy9buDFcWNJ2WULF86aOBFW6ee//vXajRsqiqOXnrXg2isuufLchdMbGzTietaQInuZbHbNmk39XV0Xn3nm+NJy3fVDSrEkxS1HdlyiKpKiUocQ0/M5JRADMx+JIQlIcRwHWgNbWVdXBw3KZDIwC/ASAVQYFUZNEJbC9xxFofFY2DRzT/35iReefw4XU4wKynwCjWccplOMLKysqAaVFXBnZpOfvOSi+pLoyldeXLf8jUmNY887+/RFF503cVytsHLCzKrEJY6Vz6WIj5/06y8vnTGh8ax5J1rJQeI6I/OneGftI8mxBrbnCophOReBS4FiwfD9lKSyKehObW3t1uA/WG3C6sTiUSZLsqwSqBsZ3ZRRm5PAWIzEGO8QRCEcyhR+oA44xH3PqagoCYVwivXrCmmorzlx7gnTp06RZdbZ2WlbTixeyn1ZlnTXEa7jWx7NZHOMuCfOnty2Z9Py11+oLg4tOu+MU2YdVx5RnFzSzuexE+HOmE7eiARXDYlIb7z4zPHjqy89d4GbGxbCYxojkkOoJRGTUVcIbGSqUKJSbqjMsXOYPWcS1WSXkBVvryJYIsLKS8pxyEJ3sMVKyssi0bgDtwkUBxwxSqUjAHEjoIL9HVhh7qOIJIli7zeOq2eMW1a+q6Ozo6MDr8RhkrDt9+/vyOeg3prgUiwWp7IiMRlK7tq5rv17XTszbfKEqZOaFOpTz2K+K0tEU2VFkRAI4bZtlpSUrV65qqmh/rwzT0v29+Ijquc7rg92AlDiAaQQKA4wIRihmmokk1nGZMFJJuNtXLcBIpaVlMNl27ZlO7Zb3syWl+MNUR3cDjTFpiTv6AQ0A2V/j4JuEsTs8BMkgMO59/91PQ41mdA8mTEVapJK5xLJTHnFmGi0yLSdzq5eJstMUuDRMqo4tgtbMDQ4kMuk6+tqp02dUl5WSgnBsR8oo+96tmPnTTNrerZHoUWcvP32unAk1tzcDGMXjRYNDQU+OlRA4GsKWkIwcII4APLUtDxNC+tahAlJp2Tj6o393QdnHDd95Gzdun2boii+bU9unlAzpty3HXwzAEFH42iyBOUFEFgKsIOYBQON4i+oD3EbGhpUVaUSw/qk02nYbCMcxabct2+f6/iUSoTSvB188BWEg7FoLFRSEsdhh6F830dNaD4sBRIAYwz7F1ncbJGdOXMm9AiFIJdzrshaQb/QFKMDI4kgFgRZhhF1XfZdjqLnn3lWpgzmORaOpFIpmGfD0CVFnjt7BpTGs3BJRrUjQAtgJItEgBFekAI7iIMBSDAM0u+JIxVGEkSRsfwS3l1UVYxxLHt4eBgX5eHhweOnT4Xm7N27d/uOrVoomBKmaoSC7zPFRVFA+G4OLzJcR6aEch8UhnXDMMJAJBJDjB3juf78eadIeKno+dFYnFAJ2mS5Hm68pKA4gfSUiYKtRUwIw2XQcux01jJCaltb34oVK7ByssyKS4q6u7so82EHxlSWzZ59PD6KMEaY4CzoC92BAR6oD+UQqKA4UJ9DJPDDOoZpHyo6xh+oDPfccCQ0e/ZMI6R5mHYug8KFCxdWVY0xzdy6dWtd1xUEp4oHjpBwHAtaI8uyokpcQFGCckxMCAG7vn79+i1btrS0tPb1HYRarX57LT7qr179dmtr286du9ra2uJFxZblgItD8woEhdiHkMvlcLCijMrkj08+3tV3YExVxelnLIDSgSDh+6nk4OyZMxob6l3PkiAAZk4oAR+I0QwIuEJvSB0C2DmUCkY9knwngdqHMdL4SFyoY1mWa5nz551UWV6mqxqy6Uyqt+dASNNDYX3fvtYtWzZxKjh0xrVhaxSZEe5bsN6WCS1TFYUS4rp+Pm+Bl1WrVq9du27zpq27du7p6en761+e2dPStvrtda372pe+9Mrb69cb4UgubwarTBkHoASHAXHAt64pRkTfsHXHE395gioyVSXoRWtry/DQIG5quiqfc9aZClwnXeHEF4W26GckgZgEG+jwfNFjkIeWHUGh6FgjwWJFxRgkncs3NDaHInHP5739A3tb237+i18f6O3zORlKp99atTrQFpxOkEuSfB+ncnDJVhQFOgIwKlNKI5FoUVFRcby0tKRc0wzwBaNRWlre1dWNE7C9vTMcjnZ2HACKi0sDsUWw8kGCUBLMimJ6pSUVlu0Bf3js8T0t+yKxon372x9+5Jebt27LZfOKpFaUVc07cR5ePGAI2+GC4JOLzAsx0oTgUsyC3qAE72YBvaMAzxC/FwTzg61AJJzqTPI833U9n1PT9iqqx9bWNhnh+J133/e5a28c2zhh2/a9yYzFqRaJlxFJX7tp21PPLgkXlXGqWpZj5m1ZDiwX/F9FU+5QJ2AAABAASURBVF3PY3hP5Pkob5ow6dLLrzjn/Avmn3raqaedMXvOCZ/45NULzzr70kWXXX7lJy697PJPfeYa2/NtF4vCcHgThk1KPA6DS31BPVfkTTcU1v789N+efOpZI1IiiEqEbjtif3tPXX3zJZdcddc373NsOngwnUiYihbxuARwogA+vFkigWUuKBUjHhChAuDYAJQE8fsSBFOHCxcsBXYQ1hxuTjwO/zBiuaSvL4lbueOz0vLq+aefdfGiq045/Vyc1JYrsqbPtKgeia/dvPOFpa/6XKKSJsuq53HX57blOrZXyPq6FlJ0Q1V1RdUjYegltKS0pKS0sromFi2C7pQUl8L6VFZWV1VWh0IR3xeeywWnEs4kWUUMMNWIFKlLXl7/yC9+l8q6kWiJz5VQuNR2WE1984Izzj//ostmzD6RC23Xrv2rVm5YsuS1waG04womaZKMS79iu77vEVXVCLRSgA0AqQCEBHGQJ+8EZBlBPcESiWQ6nVEUrbYW73YbcMpYppNM55avWLvsleUYafnydR0HBjnVmRKxffAQoXLYJ5okhfVQyYGeoTeWr93T1kmZAtMkKxolEqjRQ3Bu4pFYXFI1nxPKZBCXSKUcj8uqnrXsTDqHEtNyUpnscDI1nEgODCFKoZBThj6YrKI3JimESpxIm/cO/vR/fr9tT4cRrRA07PuKaRObqzlP9pTQYM7Z1da7ev32Neu279jVsX1n297W9v7BRCZnYS79A8PtHd2tULbuPlIIVEB9ClZKIOaFI6/w4B+jWCzGGIO3ls1mTdP0fV/TtLKyslgMyxvOZHKdnQd6u3taW/Zt3b5j/76OkBGmBOaGDw8nBweG8nlrx87dv/3N73JZu7gYrYrLKqpKysZwTvJ552D/oIW1EySYNqFUUXNmfnAogcKhxHAua2az2Z7uvoH+IXwggG/V3d3b09PX13uwt6cPFqqnpyeZTEMqvMm/577vLlv6isWZJ5TBwYTlcA9ESprluqBhf1d3a3tHV29fKp2VJNnQwyXFZSPvyPv7+/v6+tLptKIopRXlgpL3DFCZ9ywnYKSkpGT8+PHNTRMnTpg8edKU6upambKwYZQXxxrrqieMa6gqLwtpUjwaahhbJ1wX6Yba6pnHTz3v3LO+dON1d9x289VXfSISwScsw/F4OpvzfBGNxcc2jJtzwskzZ8+YOPm4yVOmTps+rXnCpPFNE5CePHXyuOYJ1XX1jU3N9Y3jGhvHNzaMnzR5Sml5WSxeFI5izeRMOtt7sL+ru2dfe0dra+vpp59+09e+dvWnP3XKglNnzppVN7a+urpa11Xd0AguNLLATh1bV1VbV1lbVzW2ocay84xQrDSc9UmTJjU0NBQVFQkhwAI4GgGO+SNgePCekCTJdf1c1oQS2bbtui6l1AjpJUUG7qgxQ9KYl070GTKZd+KsKy+76Dv3/Mfie755711fv/euO27+8nVXLLpw0ccv+MSVi0CxbkQnTZ42ftzEhoZxU6dPLC4tjRcrlkNCkcBADiZS8Lld7vcPDba1dQwNDlPCOOcQmjGGqwbcdDNvw06B6/Ly8nHjmsaPb66srIwXwsIzTrv8kosvu/iiKy6/5Nbbbr7zG7d/7dabF3/n7ltu+uK5Zy4YV1tVEtVKi0OV5bFYWI4Y8pjyYllmnmPB7cjlskL4oZCuaQohghBeQJBChhACvt6XIMdxstmsZVkK7JBm+L4ATcL3xtaWT500dvpxjeNqSsuL9cpSo7mxYtrkhvlzp58wc+LxU8bPmtY8sal2bHXJ+LEVVRVFEybUjB1bg/mWj4mZtrNlS1tHx4Enn3xJcNLW2vvrX//2Rz/678cee+KPf3r8L3/9a9u+fY888khZWeQPv//jfd/+DjygV994/YEHHti0adMbb7yx9MWXVqxc3dPXi9XCVoUxm9hUV6QpNSVFUyaMmz5p3NTJ46ZPaZrcXDtn2oRZU5qr4obm50V2OK6RCQ2VE8dXTmyqocTnnqvAUoZ0BV4ZTK4QmUwGdABg5F0ggTeB8veA53FFVWVVcTwXUHVNDxm+4ENDg/jYU1IcKyuLTmquh0zN42qmHVdXVYUFhZ8ooFMaEyXx4niRkUyku7oSsJo/e/RXO3d1r1278WeP/NxxxdNPPyur5NVXXydMuv66GxaecSZGyqRy27fuDIej6bS3Y8euRCIBGdKpjCwpb765HH7N0peWPf74k088/ufHHn/yj4/96YUlSzdu3JlPZeJRKR5mNWOiZTG1tEiZPqW4olSvq4xNm1C34MTpJ82cPHl8Xc2YUk2FwnoKoz4u3JxDQ0E0tgUO6HA4/I8UjCgRDv/Abo9Y75FKIxRqug61l1QF8CnxiLB9jzNqFMXynpuzTF/4vme5bs600olk0nbh7BDh5ex8KqqHejoHbvjyNx7+xW//9MTT3T39WPlnn//b3BNOHhhMTJpc1zxhMg7XxHA2l7KryseEtaJs0gqpMUMJG3r0xReXaZohBF21ak1JSdnAcGLajOO/dfc90Xjx5VdcCUdpxarVlMk4Hbft3HXXffc+/MivBrp7RD5t0GxFjAz2DVPhSAQC2p5Z+HfovsM5JxSXOIniRJAUCbvY5ZRTTdYUJnHPG5n7P8YsKKI8iIO/IwmSyedc1yWUSrIsGHW5b7lO3rbMHPhxsAySJHD3o1Sokow9LFMSDUmanJf8IV3hMvUIVRQjnM3ntu/cUVJWumHDhq4DByKRyIsvrkqn00KQ8847L5/P33334j8/8ZSVt8NGqLl5Ym93F7b2SXPnTJkyZe3qVVu2bJk5fdpll13Wsmc37mhl5aU2boJho6a+7sILz0fN46ZM2btn13DfgaqyiMxTw/37wjo31EAAKjwuHEE8CCnJQpKYzJjv+7CoMBeypOi6PmJJoE2EUIIgCoQgcRiMBOzwIA4Sh4sJQWO4v8j7vsBATFD0GFZDFbGiuKpIHNvOcn2Xi+BmLhxhUJE40Nq1d1VX28rs4I7aqlDD2JrW1n3XXPPpgf6eqcdNnj3z+D/98Q+33XrL1i2brvrEFSB/7tz6a6/7/HXXf+GGL33ua//xpWs+++lTTj3pnnu+ecF5Z55/3tmf/9w1V15xyWev+STOREw1l02eMOd420qvWvGaLIn2fXtXLH9944a3t23dMvW4CdOnT2pv3bZlw/KDB/YynpGp47qmoFhdVVAJzrxpZTnPKYpnW1lVlSVJAjXghVLqYSdDvzDV9wIjgenGE15IHImJLDP0osiyqqp4KwG+GJO559km3gQKDUGV0QQLokgMi68qTFVoLp0YPNjDfVs3lNKyOA680pJ48/hx55x9xtWf/MR/3HHruHF1d931penTmw2dDA2ReDwyaVIlNNE0XUUleBkQjYQZEUgYmlpXVzeucaymK8nEEI6tf/vMp5uamk49Zf5Xb7l57pzZB/v7GhvHzps3z7Rty8rjAyGm2tXZ7tg2Fx4Ec13XE0RSFMMIq4ruu04qlYLgmI4cTI9iXN93CSFFRTFCCjbn3VqCRyAID4SgBED+CMxcDu964JL1HOju6+sbGBgYPNjf09cHfXI49XxKmYLjUdPQpWnZqUw+Q2S9rmHmlGlnGtFayyZz5hz/5Ru/oEj03LNPHtcwtrqyNBo2ohGSGHZTKVPTSMggkkwsi1iu5/gOdnEsFkkmk5pmKIrmwrzlcqlkJpc1S0pKMH/IhlO1vm5sbU3drJmzL71k0fXXf/H8Cy6chcsEVx2HNY2fMeW4EyKRsnTaYgwkYO0UwamL+4RPFCkSjZQePHiwbV9rR2d7Op3ETm9padmzZ8/wcAKd/wMYIeDwH4oLBRykhnSVcy9vZrPZDCSDjQP9XJJdSizPy+VMDGBmc4Jj8WVZN6gSraidUtVwvMujEHdC08TjJtUL3x8aMCO6ZuYsRqiVJ5oMuXHGg/bh7u7e9o6u4eFhnFl48QZXiEmy43qpVDpvOpxTRdMJYZbtJ4Yzw4mM4BKuIMlkOm/ZUG7H9aPx4hPnnxArKzE9uby2qaym2fKUeMkYVdUpVt23ue+yAluEKdynFeWVxcVFsoxLQjbQ05BWUhrHZMmhnVSY/VERbAsVQU+MBPaJHXkEdaWUYhVQYlv5fDZrm6bH3VWb1u/v7eVMicZKInqUEQYvwHE90xWeFBrMkv4k3iKECTNsk6QSoigqJYeHO9sPdOxr371795IlL2LF1qxZ09XVtWnTps2bN8MMv/XWW6+++uqyZcueeea53/z+T4898fTzz7/0yutvvfHmyg2btre2dfb0DaQzeSZrlCmJZN7zmO2Q4eGsrBo4CQ70pRN5EiqtHMyRNF6CR4qg4wxni287Nvxm19BlzKV/cGjHrt2aoVZVjWloqMeera+vnzFjBpxpnBWY5lEAD0BQUOAloAaZQ0VIAUIIQoTr2un08OBg/3Ci33ZykkwnTpzoC75j585t27Zh2cN6OBqKYpHj8TDODEU1IkWhnMkP9Awmh1J93X0vL105cLA/lUoSwVVZggn78Y9+8OjDP/v23Xfdfddd+AC/ePHiB+5f/OP//tGDDz74ve999+GfPvLoo48++NOHf/LgT3/8f35y//3333bH7TfffMvtX//G4sXfffm114OtZ8HoWJ3dB9o7u3p6+wVhvQOJroMJIoclzRhOWSjxfT8SiZWUlHgex41k69atfb39EtY1GiWUm6ZpOyYXnqLIAOccU35PgJS/ByUEEAIft5jwPYkSQ5NlJiRYG+431tRNaBjXUFvDGN+3v23NmlXr1q3bs33n7u27u/a3tLfu3r19W1fnbjufyGST3HPH1tfFi6K6hjNVRVfVlWNOP/20uSfMlhUGH9/nbjqdzGRSZjZDuB8JGboq+65NfC85PJjA5sxmiiLhiKHj4D/3rDNPmD2rtrqqpnJMNBwaU14WjxW5tj80mB4cGO7s6l2/ccvq1RvgZK5ft2n79l2rVr796itvrV+3JZXM19Y0nHTSvLPPPltTVUxYYkRXVUWSPCi/48oSxZQDCELfAZxEhspHQN4rcAKPBvsTMfUY8dPJYeE60UioproSdwjcAMvLimPRkOA2Ew7FR07hUeEQYRGClXRy+VQ2CwoS2UwCK1ZVWTb/5BMvW3Txj3/4wx/85wP33XvPHbffcuMXr7/m3z591Scuu/yyiz920bmLLr3oM5+58ks3XvvNO2///ve+89OHfvyrX/4M2Y997NympnpF5q6bI8I2dBaP6JXlcdy3GusrJ4yvndg0duL4xqaG2oaG6pqqsgnN4044cc5pp5168vyTm5vH4wTAehDiE6w0AQ08mC/SQJB677/DWwy7DDiqDiX8EHAMII0YIJ7rmJ5r+Z7t+bbPLZ/nuZ8TPGvnh8xcAopgZnMgJW8mLXPINLEx04S6qkZlRbhePptL5PJJ28lS5saLQ1OnNJ937sJ/u+aTN33lhq/ddtMdt3/1zv+46c47vvK1m2+44QufWvTxs0+eO7U4vIdhAAAEWUlEQVShtjQekRjPeWbCTPc7+WHm5zTJVRnWIyOJlCxSKs3oUi4s22HVielezPDLStSiYjkUleUQPFZHSCbned8zSUAHf1dMOHkHR1FQSEJ9Cr9/H6HNSNFIohCja8ojEbxKkAT1XBcm0HRAFjcFsQn1CROCSQClFBJQ4jHq+9yG4iAriC8EnA4Op1aDq0c8wX1wbcM3zyZTycFksKcOZpIDmdRgPjOYzyYcM+lYGc/O+m5elTxZ8hGrMoenrkg+9S3uZiViMpHnbtrPp7mdpa4tYT1kdJ3jvul6ec/HWlq+7wKce1QU5kKOjkdm+t4xg+jv4FCdkcbIHEocViWUEJs7LvGYTFVVxg1Dg5GTZAaDJAkflFDq0YAjQiVKFCJYNBpVMSEYFe6CI0misoyjHI+FTIkqMU1VdE01VPQnKbIkMQJtkaSADvQnuON7ecfJ+J6FtOAu9x23oMWMearC8O5Fk4XKmIJ+GX5VmcoSrGhBHJlRRZHQdwEhRTGCOQTsYGpHUCh7V8QIOQT8vOvJURm0P5IbqRbEjge3y4PUHvcF5wA/HHxOXMECcMY5QbHw4Ryb8KHgNKAvuRCEEHDzbdtGIdKYDECE4MjbjuvaSDHGVEUJZqVISDNCERRJQokiyUijju/7RPi2aaE3n+PQlQWRPJ/kLS+ftzRNk3Bd9F0HNaygDheEUeg+BBkFmKAcIO8idaQ9A4tUMACKgHQQC9nQo5oaliX4bwUKhA8HEjqkyJoKVZFDqhJWFF1SNEWRFFXSVEPVDElWKcMEGA+mKklMiYSiiqRyT1h5y8yZnu1KVMbuDYUisqKBa8t2HdcXRNaNaDQWRwk2CSYKOJ6HLKEgViJBh4wzyQu0TvVkVcgykRWsEIPxkWRNhm7JRGIe920XHyDRAlIUQEYCL0x/JP33Mfv7gvfLi0M1Xdvz3UA9JCpTxiilnHPP9SGz5yHlcBfyeyPB9Tx4HC4upiCYoQcmsNKCIaChJEmKAjVBpGDbQUrOfTTE3ISgJDBp6JyguW27siyDVkXWdC1k6GFV1QRnju1jVVCOyhADwCAqigzD933OoZeBeWDBkUWFQAG4KMwQ0wEKyX8eQUEIFe9bB3IeDdSTGer7AqNzTqlEqESJRDiViCQJvGSAjTQlAXUQeApIkiKBSkjDIasgXHAfdiSYtec7XHiEchpogCAw80hTIYQPsjBVGCzEyI+wxjnxfeF5HLHgFJ3L+KDkB/OWBFGFUIgn+TaHNjoWZTLBhkJjISAeQ4YRrANBgDCEgdN3Aw+OADweAuodKT2mBNgEjqqKHgJgJ6KcEo8S3NU40kfVeb/kISEIOTrxfpX/rhyDvlOC4QBJYHQAvb3z6KgUygEUvKst8v8Eo6j6T3r5//Gjjwj6gMX9iKBjJ+gDav4/+vgjDfqAhf+IoI8I+gAGPuDxRxr0EUEfwMAHPP5Igz4i6AMY+IDHH2nQRwR9AAMf8PgjDfoAgv4/AAAA//9K99xUAAAABklEQVQDAJgavFGLOwRVAAAAAElFTkSuQmCC"

INFORMAL_NOTE = (
    "Informal here means transactions made on behalf of NUASA that did "
    "not pass through the NUASA First Bank account."
)

# NUASA brand palette (pulled from the chapter crest: navy, gold, teal)
NAVY = "#0B2545"
GOLD = "#D4AF37"
TEAL = "#1B998B"
RED = "#E4572E"
LIGHT_BG = "#F5F7FA"

# --------------------------------------------------------------------------
# STYLING
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        .main {{
            background-color: {LIGHT_BG};
        }}
        div[data-testid="stMetric"] {{
            background-color: white;
            border: 1px solid #E6E9EF;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 6px rgba(11, 37, 69, 0.06);
        }}
        div[data-testid="stMetricLabel"] {{
            color: {NAVY};
            font-weight: 600;
        }}
        .nuasa-header {{
            display: flex;
            align-items: center;
            gap: 18px;
            background: linear-gradient(90deg, {NAVY} 0%, #163A63 100%);
            padding: 22px 28px;
            border-radius: 14px;
            margin-bottom: 22px;
        }}
        .nuasa-header img {{
            height: 64px;
            width: 64px;
            border-radius: 50%;
            background: white;
            padding: 3px;
        }}
        .nuasa-header h1 {{
            color: white;
            font-size: 26px;
            margin: 0;
        }}
        .nuasa-header p {{
            color: #C9D6E8;
            margin: 2px 0 0 0;
            font-size: 14px;
        }}
        .informal-note {{
            background-color: #FFF6E5;
            border-left: 5px solid {GOLD};
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            color: #5A4600;
            margin-bottom: 16px;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {NAVY};
        }}
        section[data-testid="stSidebar"] * {{
            color: #EAF0FA !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# HEADER (logo + title)
# --------------------------------------------------------------------------
logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" alt="NUASA logo" />' if LOGO_B64 else ""
st.markdown(
    f"""
    <div class="nuasa-header">
        {logo_html}
        <div>
            <h1>NUASA Financial Dashboard</h1>
            <p>Nigerian Universities Alumni Students' Association &mdash; PAU Chapter</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# DATA LOADING & CLEANING (pandas only, no database)
# --------------------------------------------------------------------------
def _to_amount(series: pd.Series) -> pd.Series:
    """Convert a currency-formatted string column (e.g. '20,000.00') to float."""
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₦", "", regex=False)
        .str.strip()
        .replace({"": "0", "nan": "0", "None": "0"})
        .astype(float)
    )


@st.cache_data
def load_main_statement(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Withdrawal(DR)"] = _to_amount(df["Withdrawal(DR)"])
    df["Deposit(CR)"] = _to_amount(df["Deposit(CR)"])
    df["Balance"] = _to_amount(df["Balance"])

    # Flag the opening/closing balance marker rows before parsing dates
    df["Is Summary Row"] = df["Transaction Details"].str.contains(
        "Opening Balance|Closing Balance", case=False, na=False
    )

    df["Trans Date"] = pd.to_datetime(df["Trans Date"], format="%d-%b-%y", errors="coerce")
    df["Value Date"] = pd.to_datetime(df["Value Date"], format="%d-%b-%y", errors="coerce")

    # Clean up the multi-line transaction details for nicer display
    df["Transaction Details"] = df["Transaction Details"].str.replace("\n", " ", regex=False)

    # Derive a Debit/Credit Type column
    df["Type"] = "-"
    df.loc[df["Withdrawal(DR)"] > 0, "Type"] = "D"
    df.loc[df["Deposit(CR)"] > 0, "Type"] = "C"

    return df


@st.cache_data
def load_informal(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Withdrawal(DR)"] = _to_amount(df["Withdrawal(DR)"])
    df["Deposit(CR)"] = _to_amount(df["Deposit(CR)"])

    df["Value Date"] = pd.to_datetime(df["Value Date"], format="%d-%b-%y", errors="coerce")
    df["Transaction Details"] = df["Transaction Details"].str.replace("\n", " ", regex=False)

    df["Type"] = "-"
    df.loc[df["Withdrawal(DR)"] > 0, "Type"] = "D"
    df.loc[df["Deposit(CR)"] > 0, "Type"] = "C"

    return df


try:
    main_df_raw = load_main_statement(MAIN_STATEMENT_FILE)
    informal_df = load_informal(INFORMAL_FILE)
    load_error = None
except Exception as exc:  # noqa: BLE001
    main_df_raw = pd.DataFrame()
    informal_df = pd.DataFrame()
    load_error = str(exc)

if load_error:
    st.error(
        f"Could not load one of the CSV files. Make sure "
        f"'{MAIN_STATEMENT_FILE}' and '{INFORMAL_FILE}' are in the same "
        f"folder as this script.\n\nDetails: {load_error}"
    )
    st.stop()

# Real transactions only (excludes the Opening/Closing Balance marker rows)
txns_df = main_df_raw[~main_df_raw["Is Summary Row"]].copy()

# --------------------------------------------------------------------------
# SIDEBAR — FILTERS & GOAL SETTING
# --------------------------------------------------------------------------
st.sidebar.header("⚙️ Filters")

min_date = txns_df["Trans Date"].min()
max_date = txns_df["Trans Date"].max()

if pd.notna(min_date) and pd.notna(max_date):
    date_range = st.sidebar.date_input(
        "Transaction date range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
else:
    date_range = None

type_filter = st.sidebar.multiselect(
    "Transaction type",
    options=["D", "C"],
    default=["D", "C"],
    format_func=lambda x: "Debit (D)" if x == "D" else "Credit (C)",
)

search_term = st.sidebar.text_input("Search transaction details")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Goal Settings")
target_amount = st.sidebar.number_input(
    "Target closing balance (₦)", min_value=0.0, value=0.0, step=500.0, format="%.2f"
)

# Apply filters
filtered_df = txns_df.copy()
if date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Trans Date"] >= start) & (filtered_df["Trans Date"] <= end)
    ]
if type_filter:
    filtered_df = filtered_df[filtered_df["Type"].isin(type_filter)]
if search_term:
    filtered_df = filtered_df[
        filtered_df["Transaction Details"].str.contains(search_term, case=False, na=False)
    ]

# --------------------------------------------------------------------------
# KEY METRICS (based on the full, unfiltered main statement)
# --------------------------------------------------------------------------
opening_balance = main_df_raw.loc[main_df_raw["Is Summary Row"], "Balance"].iloc[0] \
    if main_df_raw["Is Summary Row"].any() else txns_df["Balance"].iloc[0]
closing_balance = main_df_raw.loc[main_df_raw["Is Summary Row"], "Balance"].iloc[-1] \
    if main_df_raw["Is Summary Row"].any() else txns_df["Balance"].iloc[-1]

total_debits = txns_df["Withdrawal(DR)"].sum()
total_credits = txns_df["Deposit(CR)"].sum()
net_flow = total_credits - total_debits

informal_credits = informal_df["Deposit(CR)"].sum()
informal_debits = informal_df["Withdrawal(DR)"].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Opening Balance", f"₦{opening_balance:,.2f}")
with col2:
    st.metric("Closing Balance", f"₦{closing_balance:,.2f}")
with col3:
    st.metric("Total Debits (D)", f"₦{total_debits:,.2f}", delta=f"-₦{total_debits:,.2f}", delta_color="inverse")
with col4:
    st.metric("Total Credits (C)", f"₦{total_credits:,.2f}", delta=f"+₦{total_credits:,.2f}")

st.caption(f"Net flow across the account: **₦{net_flow:,.2f}**  |  Informal activity on record: "
           f"₦{informal_credits:,.2f} received, ₦{informal_debits:,.2f} spent (outside the bank account).")

st.markdown("---")

# --------------------------------------------------------------------------
# GOAL PROGRESS TRACKER
# --------------------------------------------------------------------------
st.subheader("🎯 Goal Progress Tracker")

progress_pct = min(closing_balance / target_amount, 1.0) if target_amount > 0 else 0

if closing_balance >= target_amount:
    st.success(
        f"🎉 **Target Achieved!** Current balance of **₦{closing_balance:,.2f}** has cleared "
        f"the target of **₦{target_amount:,.2f}**."
    )
else:
    shortfall = target_amount - closing_balance
    st.warning(
        f"⚠️ **Target not reached yet.** Current balance is **₦{closing_balance:,.2f}**. "
        f"₦{shortfall:,.2f} more is needed to reach **₦{target_amount:,.2f}**."
    )

st.progress(progress_pct)

st.markdown("---")

# --------------------------------------------------------------------------
# TABS
# --------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📄 Full Statement",
        "💸 Debits",
        "💰 Credits",
        "📊 Balance Trend",
        "🧾 Informal Transactions",
    ]
)

display_cols = ["Trans Date", "Ref. Number", "Transaction Details", "Withdrawal(DR)", "Deposit(CR)", "Balance", "Type"]

with tab1:
    st.subheader("All Statement Records")
    st.caption(f"Showing {len(filtered_df)} of {len(txns_df)} transactions (filters applied from the sidebar).")
    st.dataframe(
        filtered_df[display_cols].sort_values("Trans Date"),
        use_container_width=True,
        hide_index=True,
    )
    csv_bytes = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", csv_bytes, "nuasa_filtered_statement.csv", "text/csv")

with tab2:
    st.subheader("Debit Transactions")
    debit_df = filtered_df[filtered_df["Type"] == "D"]
    if not debit_df.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(
                debit_df[display_cols].sort_values("Trans Date"),
                use_container_width=True,
                hide_index=True,
            )
        with c2:
            top_debits = debit_df.nlargest(5, "Withdrawal(DR)")[["Transaction Details", "Withdrawal(DR)"]]
            fig = px.bar(
                top_debits[::-1],
                x="Withdrawal(DR)",
                y="Transaction Details",
                orientation="h",
                title="Top debit transactions",
                color_discrete_sequence=[RED],
            )
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=320, yaxis_title="", xaxis_title="₦")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No debit transactions match the current filters.")

with tab3:
    st.subheader("Credit Transactions")
    credit_df = filtered_df[filtered_df["Type"] == "C"]
    if not credit_df.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(
                credit_df[display_cols].sort_values("Trans Date"),
                use_container_width=True,
                hide_index=True,
            )
        with c2:
            top_credits = credit_df.nlargest(5, "Deposit(CR)")[["Transaction Details", "Deposit(CR)"]]
            fig = px.bar(
                top_credits[::-1],
                x="Deposit(CR)",
                y="Transaction Details",
                orientation="h",
                title="Top credit transactions",
                color_discrete_sequence=[TEAL],
            )
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=320, yaxis_title="", xaxis_title="₦")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No credit transactions match the current filters.")

with tab4:
    st.subheader("Balance Profile Over Time")
    if not txns_df.empty:
        trend_df = txns_df.sort_values("Trans Date")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=trend_df["Trans Date"],
                y=trend_df["Balance"],
                mode="lines+markers",
                line=dict(color=NAVY, width=3),
                marker=dict(size=7, color=GOLD),
                fill="tozeroy",
                fillcolor="rgba(11, 37, 69, 0.08)",
                hovertemplate="%{x|%d %b %Y}<br>Balance: ₦%{y:,.2f}<extra></extra>",
                name="Balance",
            )
        )
        fig.add_hline(
            y=target_amount,
            line_dash="dash",
            line_color=RED,
            annotation_text=f"Target ₦{target_amount:,.0f}",
            annotation_position="top left",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=420,
            xaxis_title="Date",
            yaxis_title="Balance (₦)",
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

        cflow1, cflow2 = st.columns(2)
        with cflow1:
            pie = px.pie(
                names=["Debits", "Credits"],
                values=[total_debits, total_credits],
                color_discrete_sequence=[RED, TEAL],
                title="Debit vs Credit share",
                hole=0.55,
            )
            pie.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=320)
            st.plotly_chart(pie, use_container_width=True)
        with cflow2:
            daily = txns_df.groupby(txns_df["Trans Date"].dt.date).agg(
                Debits=("Withdrawal(DR)", "sum"), Credits=("Deposit(CR)", "sum")
            ).reset_index()
            bar = px.bar(
                daily,
                x="Trans Date",
                y=["Debits", "Credits"],
                barmode="group",
                color_discrete_sequence=[RED, TEAL],
                title="Daily debits vs credits",
            )
            bar.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=320, yaxis_title="₦", legend_title="")
            st.plotly_chart(bar, use_container_width=True)
    else:
        st.error("No balance data available to plot.")

with tab5:
    st.subheader("Informal Transactions")
    st.markdown(f'<div class="informal-note">ℹ️ {INFORMAL_NOTE}</div>', unsafe_allow_html=True)

    if not informal_df.empty:
        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            st.metric("Informal Credits", f"₦{informal_credits:,.2f}")
        with ic2:
            st.metric("Informal Debits", f"₦{informal_debits:,.2f}")
        with ic3:
            st.metric("Net Informal Flow", f"₦{(informal_credits - informal_debits):,.2f}")

        informal_display_cols = ["Value Date", "Transaction Details", "Withdrawal(DR)", "Deposit(CR)", "Type"]
        st.dataframe(
            informal_df[informal_display_cols].sort_values("Value Date"),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No informal transactions on record.")

st.markdown("---")
st.caption("NUASA Financial Dashboard · Built with Streamlit & pandas · Data as at " +
           datetime.now().strftime("%d %b %Y"))
