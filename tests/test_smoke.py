"""Smoke test for the (currently empty, reserved) ke package.

ke holds no functionality since issue #12's reset; this just guards that the
package stays importable and keeps CI meaningful until real content lands.
"""

import ke


def test_ke_imports():
    assert ke is not None
