# Algebraic expressions

AlgebraicExpression class aims to represent a mathematical operation with two operands.

```
result = operand1 operation operand2
```

## Operations
The supported operations are:
* **cb.SUM:**
$operand1 + operand2$

* **cb.SUB:**
$operand1 - operand2$

* **cb.MUL:**
$operand1 \cdot operand2 $

* **cb.DIV:**
$\frac{operand1}{operand2} $

* **cb.POW:**
$operand1^{operand2} $

* **cb.SQRT:**
$\sqrt{operand1}$ (operand2 is ignored)

* **cb.EQ:**:
$operand1 = operand2$ (boolean result)

* **cb.NEQ**
$operand1 \ne operand2$ (boolean result)

* **cb.COPY**:
$operand1$ (returns operand1 directly. operand2 is ignored)


## Operands
The supported operand types are:
* **Literal value**: 1,3,4.5,etc.
* **"Agnostic" numeric parameter**: The operation will be computed using the value specified in the workflow graph for this parameter. If no value is specified, the default value for the "agnostic" parameter (specified in the ontology) will be used.
* **AlgebraicOperation**: The result of the operation is used as the operand value. Hence, complex expressions can be defined by chaining AlgebraicExpressions.

