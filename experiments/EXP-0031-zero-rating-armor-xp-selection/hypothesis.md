# Competing hypotheses

## H1 — Current effective rating gates armor XP

If current/displayed armor rating is zero or negative at the hit, the receiver does not select AV11/12 even when a positive-DNAM armor item is equipped. Prediction: the exact-target hit trace omits the armor `UseSkill` route and raw Heavy/Light progress stays unchanged.

## H2 — Positive base item rating gates armor XP

The hit receiver checks the worn ARMO's base DNAM, independently of current effective/displayed rating. A positive-DNAM item remains XP-eligible when its effective rating is zero or negative; the points amount may still depend on HitData. Prediction: AV11/12 selection persists for qualifying hits while the positive-DNAM item remains worn.

## H3 — A zero-base-rating item can avoid armor XP and still protect by another effect

An item with zero base DNAM may fail the equipment selector while an independent enchantment, perk, or effect provides measurable protection. Prediction: the hit produces no AV11/12 award, while a matched attack shows reduced damage versus the unprotected control. This is a separate candidate from merely reducing the displayed rating of positive-DNAM armor.

The community report is untrusted and lacks build identity and numeric AVSK/protection captures. The GOG static result supports H2 only for that analyzed executable; it does not establish Steam behavior or H3.
