```
w = w - lr * gr

Q_new = Q_old - alpha * gr

loss = 0.5 * (q_old - (r + q(s', a'))) ^ 2

gr = 1 * (q_old - (r + q(s', a')))

Q_new = Q_old - alpha * (Q_old - (r + q(s', a')))
      = Q_old * (1 - alpha) + alpha * (r + q(s', a'))
```