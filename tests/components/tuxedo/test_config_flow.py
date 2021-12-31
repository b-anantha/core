"""Test the Tuxedo Touch config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.tuxedo.config_flow import CannotConnect
from homeassistant.components.tuxedo.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "homeassistant.components.tuxedo.config_flow._obtain_key",
        return_value=("key", "iv"),
    ), patch(
        "homeassistant.components.tuxedo.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "ip_address": "1.1.1.1",
                "name": "test-name",
                "code": "1234",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "test-name"
    assert result2["data"] == {
        "ip_address": "1.1.1.1",
        "name": "test-name",
        "code": 1234,
        "secret_key": "key",
        "initial_value": "iv",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_minimal_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "homeassistant.components.tuxedo.config_flow._obtain_key",
        return_value=("key", "iv"),
    ), patch(
        "homeassistant.components.tuxedo.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "ip_address": "1.1.1.1",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "Tuxedo Touch Controller"
    assert result2["data"] == {
        "ip_address": "1.1.1.1",
        "secret_key": "key",
        "initial_value": "iv",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_address(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "ip_address": "1.1.1.999",
            "name": "test-name",
            "code": "1234",
        },
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_address"}


async def test_form_invalid_code(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "ip_address": "1.1.1.1",
            "name": "test-name",
            "code": "0",
        },
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_code"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.tuxedo.config_flow._obtain_key",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "ip_address": "1.1.1.1",
                "name": "test-name",
                "code": "1234",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}
