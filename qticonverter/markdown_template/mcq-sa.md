type: mcq-sa

# Discrete-Time Fourier Transform Fundamentals
Understanding core DTFT concepts and their applications in signal processing

## Quiz

Which one of the following statements about the Discrete-Time Fourier Transform (DTFT) is the most accurate?

The DTFT of a discrete-time signal $x[n]$ is defined as:
$$
X(e^{j\omega}) = \sum_{n=-\infty}^{\infty} x[n]e^{-j\omega n}
$$

Consider the signal $x[n] = a^n u[n]$ where $|a| < 1$ and $u[n]$ is the unit step function.

![[signal_plot.png|600x300]]

The impulse response is shown above for  $a = 0.8$.

## Options

- The DTFT is periodic with period $2\pi$ in the frequency domain $\omega$
  ![[signal_plot.png]]
    - Score: 1
    - Remark: Correct. The DTFT has a periodicity of $2\pi$ because $e^{j(\omega + 2\pi)n} = e^{j\omega n}$ for all integer $n$. This fundamental property makes the DTFT unique among transform methods.

- The closed-form expression for $X(e^{j\omega})$ is $\frac{1}{1 + ae^{-j\omega}}$ for $|a| < 1$
    - Score: 0
    - Remark: Incorrect. The correct closed-form expression is $\frac{1}{1 - ae^{-j\omega}}$, not with a plus sign. This can be derived using the geometric series formula $\sum_{n=0}^{\infty} r^n = \frac{1}{1-r}$ for $|r| < 1$.

- The magnitude response reaches its maximum value at $\omega = 0$ and minimum at $\omega = \pi$
    - Score: 1
    - Remark: Correct. At $\omega = 0$, we have $e^{j \cdot 0} = 1$, making the denominator $|1 - a|$ minimum and thus $|X(e^{j\omega})|$ maximum. At $\omega = \pi$, the denominator becomes $|1 + a|$, which is maximum for $a > 0$, making the magnitude minimum.

- Decreasing the value of $a$ towards 0 makes the magnitude response peak sharper and narrower
    - Score: 0
    - Remark: Incorrect. The opposite is true: as $a$ decreases towards 0, the peak becomes broader and flatter. As $a$ increases towards 1, the pole moves closer to the unit circle, creating a sharper and narrower resonance peak near $\omega = 0$.

- The phase response $\angle X(e^{j\omega})$ is linear with slope $-1$ with respect to $\omega$
    - Score: 0
    - Remark: Incorrect. The phase response $\angle X(e^{j\omega}) = -\arctan\left(\frac{a\sin\omega}{1-a\cos\omega}\right)$ is nonlinear. It only approaches linearity in specific frequency regions but is generally a nonlinear function of $\omega$.

## Feedback (Optional)

### Correct Answer (Optional)

Understanding the periodicity of the DTFT is fundamental to digital signal processing. The relationship between the time-domain parameter $a$ and the frequency-domain characteristics (magnitude and phase response) demonstrates how pole locations relative to the unit circle directly control the sharpness and bandwidth of frequency response peaks. This concept is essential for designing digital filters and analyzing discrete-time systems.

### Wrong Answer (Optional)

Review the definition of DTFT and how it relates to the geometric series. Pay careful attention to the formula $\frac{1}{1 - ae^{-j\omega}}$ and understand how the denominator changes at different frequencies ($\omega = 0$ and $\omega = \pi$). Consider sketching the magnitude response for different values of $a$ to visualize how the frequency response changes as the pole location varies.

## Hint (Optional)

Remember that the DTFT is periodic with period $2\pi$, poles near the unit circle create sharp peaks, and the denominator in $\frac{1}{1 - ae^{-j\omega}}$ reaches its minimum at $\omega = 0$.

### Penalty (Mandatory if Hint present)

1