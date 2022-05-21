:::{include} ../README.md
---
relative-docs: docs/
relative-images:
---
:::


:::{toctree}
---
hidden: true
---

Overview <self>
:::

:::{toctree}
---
caption: CLI Reference
hidden: true
---

cli.md
:::

<!-- 
:::{toctree}
---
hidden: true
caption: User Guide
---

::: 
-->

<!--
The autosummary directive renders to rST,
so we must use eval-rst here
-->
:::{eval-rst}
.. raw:: html

    <div style="display: None">

.. autosummary::
   :recursive:
   :caption: API Reference
   :toctree: api/generated
   :nosignatures:

   soap

.. raw:: html

    </div>
:::
