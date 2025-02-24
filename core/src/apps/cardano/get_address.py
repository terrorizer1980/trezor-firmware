from trezor import log, wire
from trezor.messages import CardanoAddress
from trezor.ui.layouts import show_address

from apps.common import paths

from . import seed
from .address import derive_human_readable_address, validate_address_parameters
from .helpers import protocol_magics, staking_use_cases
from .helpers.paths import SCHEMA_PAYMENT, SCHEMA_STAKING
from .helpers.utils import to_account_path
from .layout import (
    ADDRESS_TYPE_NAMES,
    show_warning_address_foreign_staking_key,
    show_warning_address_pointer,
)
from .sign_tx import validate_network_info

if False:
    from trezor.messages import (
        CardanoAddressParametersType,
        CardanoGetAddress,
    )


@seed.with_keychain
async def get_address(
    ctx: wire.Context, msg: CardanoGetAddress, keychain: seed.Keychain
) -> CardanoAddress:
    address_parameters = msg.address_parameters

    await paths.validate_path(
        ctx,
        keychain,
        address_parameters.address_n,
        # path must match the PAYMENT or STAKING schema
        SCHEMA_PAYMENT.match(address_parameters.address_n)
        or SCHEMA_STAKING.match(address_parameters.address_n),
    )

    validate_network_info(msg.network_id, msg.protocol_magic)
    validate_address_parameters(address_parameters)

    try:
        address = derive_human_readable_address(
            keychain, address_parameters, msg.protocol_magic, msg.network_id
        )
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Deriving address failed")

    if msg.show_display:
        await _display_address(
            ctx, keychain, address_parameters, address, msg.protocol_magic
        )

    return CardanoAddress(address=address)


async def _display_address(
    ctx: wire.Context,
    keychain: seed.Keychain,
    address_parameters: CardanoAddressParametersType,
    address: str,
    protocol_magic: int,
) -> None:
    await _show_staking_warnings(ctx, keychain, address_parameters)

    network_name = None
    if not protocol_magics.is_mainnet(protocol_magic):
        network_name = protocol_magics.to_ui_string(protocol_magic)

    address_n = paths.address_n_to_str(address_parameters.address_n)
    await show_address(
        ctx,
        address=address,
        title="%s address" % ADDRESS_TYPE_NAMES[address_parameters.address_type],
        network=network_name,
        address_extra=address_n,
        title_qr=address_n,
    )


async def _show_staking_warnings(
    ctx: wire.Context,
    keychain: seed.Keychain,
    address_parameters: CardanoAddressParametersType,
) -> None:
    staking_type = staking_use_cases.get(keychain, address_parameters)
    if staking_type == staking_use_cases.MISMATCH:
        await show_warning_address_foreign_staking_key(
            ctx,
            to_account_path(address_parameters.address_n),
            to_account_path(address_parameters.address_n_staking),
            address_parameters.staking_key_hash,
        )
    elif staking_type == staking_use_cases.POINTER_ADDRESS:
        # ensured in _derive_shelley_address:
        assert address_parameters.certificate_pointer is not None
        await show_warning_address_pointer(ctx, address_parameters.certificate_pointer)
