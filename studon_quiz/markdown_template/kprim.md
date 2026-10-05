type: kprim
points: 2
partial_scoring: 1

# Properties of the DTFT
Four statements, each to be judged true or false

## Quiz

Consider the signal $x[n] = a^n u[n]$ with $|a| < 1$. Decide for each statement whether it is true or false.

## Options

- The DTFT is periodic in $\omega$ with period $2\pi$.
	- Score: 1
	- Remark: True. $e^{j(\omega + 2\pi)n} = e^{j\omega n}$ for every integer $n$.

- The DTFT is $\frac{1}{1 - a e^{-j\omega}}$.
	- Score: 1
	- Remark: True. A geometric series.

- The phase response is linear in $\omega$.
	- Score: 0
	- Remark: False. It is $-\arctan\frac{a\sin\omega}{1 - a\cos\omega}$.

- The energy is spread evenly over all frequencies.
	- Score: 0
	- Remark: False. For $a > 0$ it is concentrated near $\omega = 0$.

## Feedback (Optional)

### Correct Answer (Optional)

All four judged correctly.

### Wrong Answer (Optional)

Recall periodicity, the geometric series and how a pole near the unit circle shapes the spectrum.
