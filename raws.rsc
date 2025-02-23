# feb/22/2025 11:03:04 by RouterOS 7.6
# software id = ASB-CBDE
#
# model = RB5009UG+S+
# serial number = 123ABCDEF123
/queue simple
add burst-time=16s/16s comment="XXX" max-limit=1G/1G name=\
    XXX target=xxx.xxx.xxx.xxx/32
add burst-limit=10M/10M burst-threshold=5M/5M burst-time=16s/16s comment=\
    "XXX" max-limit=5M/5M name="XXX" target=\
    xxx.xxx.xxx.xxx/32
