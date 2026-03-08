type: mcq-ma

# Discrete-Time Fourier Transform Properties
Understanding DTFT properties and their applications in signal processing

## Quiz

Which of the following statements about the Discrete-Time Fourier Transform (DTFT) are correct?

The DTFT of a discrete-time signal $x[n]$ is defined as:
$$
X(e^{j\omega}) = \sum_{n=-\infty}^{\infty} x[n]e^{-j\omega n}
$$

Consider the signal $x[n] = a^n u[n]$ where $|a| < 1$ and $u[n]$ is the unit step function.

![[signal_plot.png|600x300]]

The impulse response is shown above for  $a = 0.8$.

## Options

- DTFT is periodic with period $2\pi$ in the frequency domain
	- Score: 1
	- Remark: Correct. The DTFT has a periodicity of $2\pi$ because $e^{j(\omega + 2\pi)n} = e^{j\omega n}$ for all integer $n$.

- The closed-form is $\frac{1}{1 - ae^{-j\omega}}$ for $|a| < 1$
	- Score: 1
	- Remark: Correct. This can be derived using the geometric series formula.

- Magnitude response minimum value occurs at $\omega = \pi$
	- Score: 1
	- Remark: Correct. At $\omega = \pi$, the denominator becomes maximum, making $|X(e^{j\omega})|$ minimum.

- Increasing $a$ towards 1 makes the magnitude response peak sharper
	- Score: 1
	- Remark: Correct. As $a \to 1$, the pole moves closer to the unit circle, creating a sharper resonance peak.

- The phase response is always linear with respect to $\omega$
	- Score: 0
	- Remark: Incorrect. The phase response is nonlinear: $\angle X(e^{j\omega}) = -\arctan\left(\frac{a\sin\omega}{1-a\cos\omega}\right)$.

- Energy is distributed uniformly across all frequencies
	- Score: 0
	- Remark: Incorrect. Energy is concentrated near $\omega = 0$ due to the pole location.

- Time-shift property: $Y(e^{j\omega}) = e^{-j2\omega} X(e^{j\omega})$ for $y[n] = x[n-2]$
	- Score: 1
	- Remark: Correct. This demonstrates the DTFT time-shift property.

## Feedback (Optional)

### Correct Answer (Optional)

The DTFT is a fundamental tool in digital signal processing with key properties including periodicity, linearity, and shift properties. Understanding how poles and zeros affect the frequency response is crucial for filter design and signal analysis. The magnitude response shows how different frequency components are amplified or attenuated, while the phase response indicates the phase shift at each frequency.

### Wrong Answer (Optional)

Review the definitions of DTFT, its periodicity properties, and the relationship between pole locations and frequency response characteristics. Pay special attention to the time-shift property and how parameter variations affect the magnitude and phase responses. Consider plotting DTFT magnitude responses for different values of $a$ to visualize how the frequency response changes.

## Hint (Optional)

Remember that the DTFT is periodic with period $2\pi$, poles near the unit circle create sharp peaks in magnitude response, and the time-shift property introduces a linear phase term $e^{-j\omega N}$.

### Penalty (Mandatory if Hint present)

2