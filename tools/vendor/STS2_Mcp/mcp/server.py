"""MCP server bridge for Slay the Spire 2.

Connects to the KarenSTS2MCP mod's HTTP server and exposes game actions
as MCP tools for Claude Desktop / Claude Code.
"""

import argparse
import asyncio
import json
import sys

import httpx
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("karen-sts2")

_base_url: str = "http://localhost:15527"
_trust_env: bool = True
_http: httpx.AsyncClient | None = None


def _sp_url() -> str:
    return f"{_base_url}/api/v1/singleplayer"


def _mp_url() -> str:
    return f"{_base_url}/api/v1/multiplayer"


def _profile_url() -> str:
    return f"{_base_url}/api/v1/profile"


def _compendium_url() -> str:
    return f"{_base_url}/api/v1/compendium"


def _wiki_url() -> str:
    return f"{_base_url}/api/v1/wiki"


def _profiles_url() -> str:
    return f"{_base_url}/api/v1/profiles"


def _settings_url() -> str:
    return f"{_base_url}/api/v1/settings"


def _ui_prompt_url() -> str:
    return f"{_base_url}/api/v1/ui/prompt"


def _screenshot_url() -> str:
    return f"{_base_url}/api/v1/screenshot"


def _background_url() -> str:
    return f"{_base_url}/api/v1/window/background"


def _minimize_url() -> str:
    return f"{_base_url}/api/v1/window/minimize"


def _get_client() -> httpx.AsyncClient:
    global _http
    if _http is None:
        _http = httpx.AsyncClient(timeout=httpx.Timeout(10), trust_env=_trust_env)
    return _http


async def _get(params: dict | None = None) -> str:
    r = await _get_client().get(_sp_url(), params=params)
    r.raise_for_status()
    return r.text


async def _post(body: dict) -> str:
    r = await _get_client().post(_sp_url(), json=body)
    r.raise_for_status()
    return r.text


async def _mp_get(params: dict | None = None) -> str:
    r = await _get_client().get(_mp_url(), params=params)
    r.raise_for_status()
    return r.text


async def _mp_post(body: dict) -> str:
    r = await _get_client().post(_mp_url(), json=body)
    r.raise_for_status()
    return r.text


async def _profile_get() -> str:
    r = await _get_client().get(_profile_url())
    r.raise_for_status()
    return r.text


async def _compendium_get() -> str:
    r = await _get_client().get(_compendium_url())
    r.raise_for_status()
    return r.text


async def _wiki_get(query: str, item_type: str = "all", limit: int = 10) -> str:
    r = await _get_client().get(
        _wiki_url(),
        params={"query": query, "item_type": item_type, "limit": limit},
    )
    r.raise_for_status()
    return r.text


async def _profiles_get() -> str:
    r = await _get_client().get(_profiles_url())
    r.raise_for_status()
    return r.text


async def _profiles_post(body: dict) -> str:
    r = await _get_client().post(_profiles_url(), json=body)
    r.raise_for_status()
    return r.text


async def _wait_for_profile(profile_id: int, fallback: str) -> str:
    last_profiles: dict | None = None
    for _ in range(30):
        await asyncio.sleep(0.1)
        profiles_text = await _profiles_get()
        profiles = json.loads(profiles_text)
        last_profiles = profiles
        if profiles.get("current_profile_id") == profile_id:
            return json.dumps(
                {
                    "status": "ok",
                    "message": f"Switched to profile {profile_id}",
                    "current_profile_id": profile_id,
                    "profiles": profiles.get("profiles", []),
                },
                indent=2,
            )

    return json.dumps(
        {
            "status": "error",
            "error": f"Timed out waiting for profile {profile_id} to become active",
            "current_profile_id": (
                last_profiles.get("current_profile_id")
                if isinstance(last_profiles, dict)
                else None
            ),
            "profiles": (
                last_profiles.get("profiles", [])
                if isinstance(last_profiles, dict)
                else []
            ),
            "initial_response": fallback,
        },
        indent=2,
    )


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.ConnectError):
        return "Error: Cannot connect to KarenSTS2MCP mod. Is the game running with the mod enabled?"
    if isinstance(e, httpx.HTTPStatusError):
        return f"Error: HTTP {e.response.status_code} — {e.response.text}"
    return f"Error: {e}"


# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_game_state(format: str = "markdown") -> str:
    """Get the current Slay the Spire 2 game state.

    Returns the full game state including player stats, hand, enemies, potions, etc.
    The state_type field indicates the current screen (combat, map, event, shop,
    fake_merchant, etc.).

    Blocking first-launch notices, tutorials and popups take priority over the
    underlying screen. Use get_ui_prompt / handle_ui_prompt for their options,
    or dismiss_tutorials to disable and advance onboarding in a bounded loop.

    player.hand contains cards. A card with type="Power" is a playable Power
    card. player.status and battle.enemies[].status contain powers (effects
    already attached to creatures), not cards. Card IDs and power IDs are
    separate; type="Status" on a card is also a card type, not a power effect.

    Args:
        format: "markdown" for human-readable output, "json" for structured data.
    """
    try:
        return await _get({"format": format})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_ui_prompt() -> str:
    """Read the current blocking tutorial, first-launch notice or modal popup.

    Works before starting a run and in both singleplayer and multiplayer.
    Returns active=false if there is no prompt; otherwise includes prompt_id,
    prompt_type, menu_screen, body, ready and options with their enabled flags.
    If ready=false, wait and poll; do not call gameplay actions underneath it.
    """
    try:
        r = await _get_client().get(_ui_prompt_url())
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def handle_ui_prompt(option: str, prompt_id: str | None = None) -> str:
    """Choose an enabled option from get_ui_prompt, using the game's own button.

    Pass the latest prompt_id to reject a replaced popup or changed tutorial page.
    Typical options: yes/no for tutorial consent and confirmation popups,
    advance/proceed for tutorials, proceed for the Early Access notice.
    Advances one step only; read fresh state after each action. Does not fall
    through to a menu/gameplay action when no prompt exists. Works in co-op too.
    """
    body = {"option": option}
    if prompt_id is not None:
        body["prompt_id"] = prompt_id
    try:
        r = await _get_client().post(_ui_prompt_url(), json=body)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def dismiss_tutorials(max_steps: int = 20) -> str:
    """Disable future tutorials and advance currently open onboarding prompts.

    Saves skip_tutorial=true for the current profile and skip_first_prompt=true.
    Uses native buttons so waiting game callbacks still finish. Handles tutorial
    consent, multi-page tutorials and the Early Access notice, in either mode.
    Stops at unrelated confirmation popups without choosing for you.

    max_steps: 1-100 polling/advance attempts (0.2 seconds between attempts).
    Returns completed when no prompt is active, blocked for an unrelated choice,
    or waiting at the limit. Inspect the returned prompt and poll/retry if waiting;
    this call does not monitor prompts that appear later in the run.
    """
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 100:
        return json.dumps({"status": "error", "error": "max_steps must be an integer between 1 and 100"})
    actions = 0
    try:
        r = await _get_client().post(_settings_url(), json={"skip_tutorial": True, "skip_first_prompt": True})
        r.raise_for_status()
        settings = r.json()
        if settings.get("error") or settings.get("status") == "error":
            return r.text
        for step in range(max_steps + 1):
            r = await _get_client().get(_ui_prompt_url())
            r.raise_for_status()
            prompt = r.json()
            if prompt.get("error") or prompt.get("status") == "error":
                return r.text
            if prompt.get("active") is False:
                return json.dumps({"status": "completed", "actions_taken": actions, "prompt": prompt})
            if prompt.get("active") is not True:
                return json.dumps({"status": "error", "error": "Invalid prompt response", "prompt": prompt})
            screen = prompt.get("menu_screen")
            option = {"tutorial_prompt": "no", "tutorial": "advance", "early_access_disclaimer": "proceed"}.get(screen)
            if option is None:
                return json.dumps({"status": "blocked", "reason": "Explicit popup choice required", "actions_taken": actions, "prompt": prompt})
            if step == max_steps:
                return json.dumps({"status": "waiting", "reason": "Step limit reached; inspect prompt and poll/retry", "actions_taken": actions, "prompt": prompt})
            if any(item.get("name") == option and item.get("enabled") is True for item in prompt.get("options", [])):
                # A stale ID yields an error instead of clicking a newly appeared dialog.
                if not prompt.get("prompt_id"):
                    return json.dumps({"status": "error", "error": "Missing prompt_id", "prompt": prompt})
                r = await _get_client().post(_ui_prompt_url(), json={"option": option, "prompt_id": prompt["prompt_id"]})
                r.raise_for_status()
                result = r.json()
                if result.get("error") or result.get("status") != "ok":
                    return r.text
                actions += 1
            await asyncio.sleep(0.2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def menu_select(option: str, seed: str | None = None) -> str:
    """Select a visible menu option.

    Use with state_type "menu" or "game_over". Covers main-menu navigation,
    singleplayer / multiplayer submenus, multiplayer host & join lobbies,
    multiplayer load lobby (resume saved co-op run), character select for SP
    and MP (with `unready` once readied in MP), profile switching, timeline
    controls, tutorial prompts, blocking popups, and game-over main-menu return.

    Multiplayer flow tips:
      - On menu_screen "multiplayer_join", use refresh / back / join_<index> /
        join_<player_id> (e.g. "join_0" or "join_76561198000000000").
      - On menu_screen "multiplayer_load_lobby", use confirm (or embark) to
        ready up; the run resumes once everyone is connected and ready.
      - On menu_screen "character_select" while in MP, the state includes a
        `lobby` block with the roster, ready states, and ascension; "unready"
        becomes available after you confirm/embark.

    Args:
        option: Option ID from the current menu state's options list. If an
            option is listed under blocked_options, selecting it returns the
            API's manual-action response instead of forcing UI entry.
        seed: Optional seed for supported embark flows. Standard mode rejects seeds.
    """
    body: dict = {"action": "menu_select", "option": option}
    if seed is not None:
        body["seed"] = seed
    try:
        return await _post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_screenshot() -> Image:
    """Capture the current game viewport as a PNG image, including menus and co-op."""
    try:
        r = await _get_client().get(_screenshot_url())
        r.raise_for_status()
        return Image(data=r.content, format="png")
    except Exception as e:
        raise RuntimeError(_handle_error(e)) from e


@mcp.tool()
async def background_game() -> str:
    """Minimize the game window; alias of minimize_game()."""
    try:
        r = await _get_client().post(_background_url())
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def minimize_game() -> str:
    """Minimize the game window so MCP tests do not interrupt other desktop work."""
    try:
        r = await _get_client().post(_minimize_url())
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def run_command(command: str) -> str:
    """Execute a Slay the Spire 2 developer console command in the active run.

    Singleplayer only; syntax matches the in-game developer console.

    Cards and powers are different models with separate IDs:
    - `card <CARD_ID> [pile]` spawns a card, without playing it. Default pile is
      Hand (combat only); Deck adds to the current run's deck. Example:
      `card INFLAME Hand`. Read fresh player.hand indices before playing it
      with combat_play_card. A card with type="Power" is still a card;
      type="Status" also denotes a card type.
    - `power <POWER_ID> <amount> <target-index>` directly applies a creature
      effect during combat, without creating a card. Example:
      `power STRENGTH_POWER 2 0` applies strength to creature-list index 0.
      The target is the zero-based index in CombatState.Creatures, NOT an
      entity_id, combat_id, hand index or battle.enemies index. Index 0 is
      illustrative, not guaranteed to be the player. Current MCP state does
      not expose this index; verify ordering instead of guessing.

    INFLAME is a Power-type card; it applies the separate STRENGTH_POWER effect
    when played. Never substitute a card ID for a power ID. Existing effects
    appear in player.status / battle.enemies[].status. search_wiki searches
    cards/relics, not power effects. Use `help card` / `help power` for syntax.

    `unlock all` persistently unlocks the active profile's discoveries,
    timeline epochs and ascensions; it does not grant inventory items or all
    platform achievements. `travel` toggles free map travel, so check
    map.travel_mode_enabled before calling it. Poll state after async=true.
    """
    try:
        return await _post({"action": "run_command", "command": command})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def abandon_run() -> str:
    """Immediately abandon the active singleplayer run, ending it permanently.

    Uses the game's Give Up flow without an additional confirmation popup.
    No pause menu navigation is required. Returns async=true while the game
    resolves the loss; poll get_game_state until state_type is game_over, then
    call menu_select("main_menu") to return. Does not abandon saved runs from
    the main menu and does not support multiplayer.
    """
    try:
        return await _post({"action": "abandon_run"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def close_settings() -> str:
    """Close the visible settings screen with its Back button."""
    try:
        return await _post({"action": "close_settings"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_game_settings() -> str:
    """Read display, audio, tutorial, and first-launch prompt settings."""
    try:
        r = await _get_client().get(_settings_url())
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def set_game_settings(
    fullscreen: bool | None = None,
    muted: bool | None = None,
    skip_tutorial: bool | None = None,
    skip_first_prompt: bool | None = None,
    window_width: int | None = None,
    window_height: int | None = None,
) -> str:
    """Change game settings and save them immediately.

    Supply only the settings to change. Window width and height must be supplied
    together in pixels (320x240 to 7680x4320); setting them switches to windowed
    mode. The first-launch prompt is the Early Access disclaimer.
    skip_tutorial prevents future tutorials; existing tutorial callbacks may
    still need advancing. Use dismiss_tutorials() to finish them, or inspect the
    returned ui_prompt and use handle_ui_prompt for individual steps.
    """
    body = {
        name: value for name, value in {
            "fullscreen": fullscreen,
            "muted": muted,
            "skip_tutorial": skip_tutorial,
            "skip_first_prompt": skip_first_prompt,
            "window_width": window_width,
            "window_height": window_height,
        }.items() if value is not None
    }
    try:
        r = await _get_client().post(_settings_url(), json=body)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_profile() -> str:
    """Get the current profile's persistent progress summary.

    Includes character stats, discovered content, achievements, epochs, and global
    run totals for the active profile.
    """
    try:
        return await _profile_get()
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_compendium() -> str:
    """Get the active profile's Compendium-shaped progress summary.

    Mirrors the visible Compendium cards: Card Library, Relic Collection,
    Potion Lab, Bestiary, Character Stats, and Run History. This is a
    profile-level view, so it is useful at the main menu as well as during a run.
    Card/relic/potion rules text is still supplied by game state when those
    objects are visible in run-specific contexts.
    """
    try:
        return await _compendium_get()
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def search_wiki(query: str, item_type: str = "all", limit: int = 10) -> str:
    """Search discovered card and relic wiki entries for the active profile.

    Uses fuzzy matching over profile-unlocked content only, so agents can ask
    for a card or relic by approximate name without receiving the entire game
    catalog. Card results include both base and upgraded variants when the card
    can be upgraded.

    Power-type cards are included as cards. Creature powers/status effects
    (PowerModel) are not searchable here; do not use card IDs as power IDs.

    Args:
        query: Search text such as "ironclad perfect strike" or "silver spoon".
        item_type: "all", "card", or "relic".
        limit: Maximum results to return. Defaults to 10; the mod clamps it to
            a bounded maximum.
    """
    try:
        return await _wiki_get(query, item_type, limit)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def list_profiles() -> str:
    """List the three profile slots and identify the active slot.

    The has_data field indicates whether a slot currently has progress data.
    """
    try:
        return await _profiles_get()
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def switch_profile(profile_id: int) -> str:
    """Switch to a profile slot through the game's profile UI.

    Use an empty slot to create or enter a fresh profile for testing. This cannot
    be used while a run is in progress.

    Args:
        profile_id: Profile slot to switch to. Must be 1, 2, or 3.
    """
    try:
        body = {"action": "switch", "profile_id": profile_id}
        result = await _profiles_post(body)
        try:
            parsed = json.loads(result)
            if parsed.get("status") == "error":
                return result

            message = parsed.get("message", "")
            if isinstance(message, str) and message.startswith("Opened profile screen"):
                for _ in range(20):
                    await asyncio.sleep(0.1)
                    state_text = await _get({"format": "json"})
                    state = json.loads(state_text)
                    if state.get("menu_screen") == "profile_select":
                        result = await _profiles_post(body)
                        parsed = json.loads(result)
                        if parsed.get("status") == "error":
                            return result
                        break
            result = await _wait_for_profile(profile_id, result)
        except json.JSONDecodeError:
            pass
        return result
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def delete_profile(profile_id: int) -> str:
    """Delete an inactive profile slot.

    The active profile cannot be deleted through this tool. Switch away first if
    you intend to remove a slot after backing up any data you need.

    Args:
        profile_id: Profile slot to delete. Must be 1, 2, or 3.
    """
    try:
        return await _profiles_post({"action": "delete", "profile_id": profile_id})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def use_potion(slot: int, target: str | None = None) -> str:
    """Use a potion from the player's potion slots.

    Works both during and outside of combat. Combat-only potions require an active battle.

    Args:
        slot: Potion slot index (as shown in game state).
        target: Entity ID of the target enemy (e.g. "JAW_WORM_0"). Required for enemy-targeted potions.
    """
    body: dict = {"action": "use_potion", "slot": slot}
    if target is not None:
        body["target"] = target
    try:
        return await _post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def discard_potion(slot: int) -> str:
    """Discard a potion from the player's potion slots to free up space.

    Use this when all potion slots are full and you need room for incoming potions
    (e.g. before collecting a potion reward).

    Args:
        slot: Potion slot index to discard (as shown in game state).
    """
    try:
        return await _post({"action": "discard_potion", "slot": slot})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def proceed_to_map() -> str:
    """Proceed from the current screen to the map.

    Works from: rewards screen, rest site, shop, fake merchant.
    Does NOT work for events — use event_choose_option() with the Proceed option's index.
    """
    try:
        return await _post({"action": "proceed"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Combat (state_type: monster / elite / boss)
# ---------------------------------------------------------------------------


@mcp.tool()
async def combat_hover_card(card_index: int, target: str | None = None) -> str:
    """Hover a hand card without playing it or spending energy.

    card_index: 0-based hand index. Omit target to inspect any hand card,
    including a card requiring a target. For a single-enemy card, pass an enemy
    entity_id to preview its target-dependent values. Does not start dragging
    or targeting. Use combat_unhover_card to clear the preview.
    """
    body: dict = {"action": "hover_card", "card_index": card_index}
    if target is not None:
        body["target"] = target
    try:
        return await _post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def combat_unhover_card() -> str:
    """Clear the card hover/target preview created by combat_hover_card."""
    try:
        return await _post({"action": "unhover_card"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def combat_play_card(card_index: int, target: str | None = None) -> str:
    """[Combat] Play a card from the player's hand.

    Args:
        card_index: Index of the card in hand (0-based, as shown in game state).
        target: Entity ID of the target enemy (e.g. "JAW_WORM_0"). Required for single-target cards.

    Note that the index can change as cards are played - playing a card will shift the indices of remaining cards in hand.
    Refer to the latest game state for accurate indices. New cards are drawn to the right, so playing cards from right to left can help maintain more stable indices for remaining cards.
    """
    body: dict = {"action": "play_card", "card_index": card_index}
    if target is not None:
        body["target"] = target
    try:
        return await _post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def combat_end_turn() -> str:
    """[Combat] End the player's current turn."""
    try:
        return await _post({"action": "end_turn"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# In-Combat Card Selection (state_type: hand_select)
# ---------------------------------------------------------------------------


@mcp.tool()
async def combat_select_card(card_index: int) -> str:
    """[Combat Selection] Select a card from hand during an in-combat card selection prompt.

    Used when a card effect asks you to select a card to exhaust, discard, etc.
    This is different from deck_select_card which handles out-of-combat card selection overlays.

    Args:
        card_index: 0-based index of the card in the selectable hand cards (as shown in game state).
    """
    try:
        return await _post({"action": "combat_select_card", "card_index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def combat_confirm_selection() -> str:
    """[Combat Selection] Confirm the in-combat card selection.

    After selecting the required number of cards from hand (exhaust, discard, etc.),
    use this to confirm the selection. Only works when the confirm button is enabled.
    """
    try:
        return await _post({"action": "combat_confirm_selection"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Rewards (state_type: rewards / card_reward)
# ---------------------------------------------------------------------------


@mcp.tool()
async def rewards_claim(reward_index: int) -> str:
    """[Rewards] Claim a reward from the post-combat rewards screen.

    Gold, potion, and relic rewards are claimed immediately.
    Card rewards open the card selection screen (state changes to card_reward).

    Args:
        reward_index: 0-based index of the reward on the rewards screen.

    Note that claiming a reward may change the indices of remaining rewards, so refer to the latest game state for accurate indices.
    Claiming from right to left can help maintain more stable indices for remaining rewards, as rewards will always shift left to fill in gaps.
    """
    try:
        return await _post({"action": "claim_reward", "index": reward_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def rewards_pick_card(card_index: int) -> str:
    """[Rewards] Select a card from the card reward selection screen.

    Args:
        card_index: 0-based index of the card to add to the deck.
    """
    try:
        return await _post({"action": "select_card_reward", "card_index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def rewards_skip_card() -> str:
    """[Rewards] Skip the card reward without selecting a card."""
    try:
        return await _post({"action": "skip_card_reward"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Map (state_type: map)
# ---------------------------------------------------------------------------


@mcp.tool()
async def map_choose_node(node_index: int) -> str:
    """[Map] Choose a map node to travel to.

    With developer travel mode enabled, next_options includes every map room.
    Read fresh state after toggling travel mode, as node indices may change.

    Args:
        node_index: 0-based index of the node from the next_options list.
    """
    try:
        return await _post({"action": "choose_map_node", "index": node_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def map_enter_room(col: int, row: int) -> str:
    """[Map] Enter any room on the current act's map by its coordinates.

    Singleplayer only. Requires an open map and developer travel mode enabled
    via run_command("travel"). That command toggles the mode: check
    map.travel_mode_enabled first. Includes visited, disconnected, and boss
    nodes. Read game state after calling to wait for travel to finish.

    Args:
        col: Exact column from map.nodes or map.next_options (not a list index).
        row: Exact row from map.nodes or map.next_options (not the floor number).
    """
    try:
        return await _post({"action": "enter_map_room", "col": col, "row": row})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Rest Site (state_type: rest_site)
# ---------------------------------------------------------------------------


@mcp.tool()
async def rest_choose_option(option_index: int) -> str:
    """[Rest Site] Choose a rest site option (rest, smith, etc.).

    Args:
        option_index: 0-based index of the option from the rest site state.
    """
    try:
        return await _post({"action": "choose_rest_option", "index": option_index})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Shop (state_type: shop)
# ---------------------------------------------------------------------------


@mcp.tool()
async def shop_purchase(item_index: int) -> str:
    """[Shop / Fake Merchant] Purchase an item from the shop.

    Works for both regular shops (state_type: shop) and the fake merchant
    event (state_type: fake_merchant). The fake merchant only sells relics.

    Args:
        item_index: 0-based index of the item from the shop state.
    """
    try:
        return await _post({"action": "shop_purchase", "index": item_index})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Event (state_type: event)
# ---------------------------------------------------------------------------


@mcp.tool()
async def event_choose_option(option_index: int) -> str:
    """[Event] Choose an event option.

    Works for both regular events and ancients (after dialogue ends).
    Also used to click the Proceed option after an event resolves.

    Args:
        option_index: 0-based index of the option from the event state.
    """
    try:
        return await _post({"action": "choose_event_option", "index": option_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def event_advance_dialogue() -> str:
    """[Event] Advance ancient event dialogue.

    Click through dialogue text in ancient events. Call repeatedly until options appear.
    """
    try:
        return await _post({"action": "advance_dialogue"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Card Selection (state_type: card_select)
# ---------------------------------------------------------------------------


@mcp.tool()
async def deck_select_card(card_index: int) -> str:
    """[Card Selection] Select or deselect a card in the card selection screen.

    Used when the game asks you to choose cards from your deck (transform, upgrade,
    remove, discard) or pick a card from offered choices (potions, effects).

    For deck selections: toggles card selection. For choose-a-card: picks immediately.

    Args:
        card_index: 0-based index of the card (as shown in game state).
    """
    try:
        return await _post({"action": "select_card", "index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def deck_confirm_selection() -> str:
    """[Card Selection] Confirm the current card selection.

    After selecting the required number of cards, use this to confirm.
    If a preview is showing (e.g., transform preview), this confirms the preview.
    Not needed for choose-a-card screens where picking is immediate.
    """
    try:
        return await _post({"action": "confirm_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def deck_cancel_selection() -> str:
    """[Card Selection] Cancel the current card selection.

    If a preview is showing, goes back to the selection grid.
    For choose-a-card screens, clicks the skip button (if available).
    Otherwise, closes the card selection screen (only if cancellation is allowed).
    """
    try:
        return await _post({"action": "cancel_selection"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Bundle Selection (state_type: bundle_select)
# ---------------------------------------------------------------------------


@mcp.tool()
async def bundle_select(bundle_index: int) -> str:
    """[Bundle Selection] Open a bundle preview.

    Args:
        bundle_index: 0-based index of the bundle.
    """
    try:
        return await _post({"action": "select_bundle", "index": bundle_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def bundle_confirm_selection() -> str:
    """[Bundle Selection] Confirm the currently previewed bundle."""
    try:
        return await _post({"action": "confirm_bundle_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def bundle_cancel_selection() -> str:
    """[Bundle Selection] Cancel the current bundle preview."""
    try:
        return await _post({"action": "cancel_bundle_selection"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Relic Selection (state_type: relic_select)
# ---------------------------------------------------------------------------


@mcp.tool()
async def relic_select(relic_index: int) -> str:
    """[Relic Selection] Select a relic from the relic selection screen.

    Used when the game offers a choice of relics (e.g., boss relic rewards).

    Args:
        relic_index: 0-based index of the relic (as shown in game state).
    """
    try:
        return await _post({"action": "select_relic", "index": relic_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def relic_skip() -> str:
    """[Relic Selection] Skip the relic selection without choosing a relic."""
    try:
        return await _post({"action": "skip_relic_selection"})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Treasure (state_type: treasure)
# ---------------------------------------------------------------------------


@mcp.tool()
async def treasure_claim_relic(relic_index: int) -> str:
    """[Treasure] Claim a relic from the treasure chest.

    The chest is auto-opened when entering the treasure room.
    After claiming, use proceed_to_map() to continue.

    Args:
        relic_index: 0-based index of the relic (as shown in game state).
    """
    try:
        return await _post({"action": "claim_treasure_relic", "index": relic_index})
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Crystal Sphere (state_type: crystal_sphere)
# ---------------------------------------------------------------------------


@mcp.tool()
async def crystal_sphere_set_tool(tool: str) -> str:
    """[Crystal Sphere] Switch the active divination tool.

    Args:
        tool: Either "big" or "small".
    """
    try:
        return await _post({"action": "crystal_sphere_set_tool", "tool": tool})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def crystal_sphere_click_cell(x: int, y: int) -> str:
    """[Crystal Sphere] Click a hidden cell on the Crystal Sphere grid.

    Args:
        x: Cell x-coordinate.
        y: Cell y-coordinate.
    """
    try:
        return await _post({"action": "crystal_sphere_click_cell", "x": x, "y": y})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def crystal_sphere_proceed() -> str:
    """[Crystal Sphere] Continue after the Crystal Sphere minigame finishes."""
    try:
        return await _post({"action": "crystal_sphere_proceed"})
    except Exception as e:
        return _handle_error(e)


# ===========================================================================
# MULTIPLAYER tools — all route through /api/v1/multiplayer
# ===========================================================================


@mcp.tool()
async def mp_get_game_state(format: str = "markdown") -> str:
    """[Multiplayer] Get the current multiplayer game state.

    Returns a summary of all players (HP, gold, alive status) plus full
    detail for the local player (relics, potions, deck, etc.), along with
    multiplayer-specific data: map votes, event votes, treasure bids,
    end-turn ready status. Only works during a multiplayer run.

    Args:
        format: "markdown" for human-readable output, "json" for structured data.
    """
    try:
        return await _mp_get({"format": format})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_hover_card(card_index: int, target: str | None = None) -> str:
    """[Multiplayer] Hover a local hand card, optionally previewing an enemy target.

    Same preview behavior as combat_hover_card; does not play or enqueue a card.
    """
    body: dict = {"action": "hover_card", "card_index": card_index}
    if target is not None:
        body["target"] = target
    try:
        return await _mp_post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_unhover_card() -> str:
    """[Multiplayer] Clear the local card hover/target preview."""
    try:
        return await _mp_post({"action": "unhover_card"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_play_card(card_index: int, target: str | None = None) -> str:
    """[Multiplayer Combat] Play a card from the local player's hand.

    Same as singleplayer combat_play_card but routed through the multiplayer
    endpoint for sync safety.

    Args:
        card_index: Index of the card in hand (0-based).
        target: Entity ID of the target enemy (e.g. "JAW_WORM_0"). Required for single-target cards.
    """
    body: dict = {"action": "play_card", "card_index": card_index}
    if target is not None:
        body["target"] = target
    try:
        return await _mp_post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_end_turn() -> str:
    """[Multiplayer Combat] Submit end-turn vote.

    In multiplayer, ending the turn is a VOTE — the turn only ends when ALL
    players have submitted. Use mp_combat_undo_end_turn() to retract.
    """
    try:
        return await _mp_post({"action": "end_turn"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_undo_end_turn() -> str:
    """[Multiplayer Combat] Retract end-turn vote.

    If you submitted end turn but want to play more cards, use this to undo.
    Only works if other players haven't all committed yet.
    """
    try:
        return await _mp_post({"action": "undo_end_turn"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_use_potion(slot: int, target: str | None = None) -> str:
    """[Multiplayer] Use a potion from the local player's potion slots.

    Args:
        slot: Potion slot index (as shown in game state).
        target: Entity ID of the target enemy. Required for enemy-targeted potions.
    """
    body: dict = {"action": "use_potion", "slot": slot}
    if target is not None:
        body["target"] = target
    try:
        return await _mp_post(body)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_discard_potion(slot: int) -> str:
    """[Multiplayer] Discard a potion from the local player's potion slots to free up space.

    Args:
        slot: Potion slot index to discard (as shown in game state).
    """
    try:
        return await _mp_post({"action": "discard_potion", "slot": slot})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_map_vote(node_index: int) -> str:
    """[Multiplayer Map] Vote for a map node to travel to.

    In multiplayer, map selection is a vote — travel happens when all players
    agree. Re-voting for the same node sends a ping to other players.

    Args:
        node_index: 0-based index of the node from the next_options list.
    """
    try:
        return await _mp_post({"action": "choose_map_node", "index": node_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_event_choose_option(option_index: int) -> str:
    """[Multiplayer Event] Choose or vote for an event option.

    For shared events: this is a vote (resolves when all players vote).
    For individual events: immediate choice, same as singleplayer.

    Args:
        option_index: 0-based index of the option from the event state.
    """
    try:
        return await _mp_post({"action": "choose_event_option", "index": option_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_event_advance_dialogue() -> str:
    """[Multiplayer Event] Advance ancient event dialogue."""
    try:
        return await _mp_post({"action": "advance_dialogue"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_rest_choose_option(option_index: int) -> str:
    """[Multiplayer Rest Site] Choose a rest site option (rest, smith, etc.).

    Per-player choice — no voting needed.

    Args:
        option_index: 0-based index of the option.
    """
    try:
        return await _mp_post({"action": "choose_rest_option", "index": option_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_shop_purchase(item_index: int) -> str:
    """[Multiplayer Shop] Purchase an item from the shop.

    Per-player inventory — no voting needed.

    Args:
        item_index: 0-based index of the item.
    """
    try:
        return await _mp_post({"action": "shop_purchase", "index": item_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_rewards_claim(reward_index: int) -> str:
    """[Multiplayer Rewards] Claim a reward from the post-combat rewards screen.

    Args:
        reward_index: 0-based index of the reward.
    """
    try:
        return await _mp_post({"action": "claim_reward", "index": reward_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_rewards_pick_card(card_index: int) -> str:
    """[Multiplayer Rewards] Select a card from the card reward screen.

    Args:
        card_index: 0-based index of the card to add to the deck.
    """
    try:
        return await _mp_post({"action": "select_card_reward", "card_index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_rewards_skip_card() -> str:
    """[Multiplayer Rewards] Skip the card reward."""
    try:
        return await _mp_post({"action": "skip_card_reward"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_proceed_to_map() -> str:
    """[Multiplayer] Proceed from the current screen to the map.

    Works from: rewards screen, rest site, shop.
    """
    try:
        return await _mp_post({"action": "proceed"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_deck_select_card(card_index: int) -> str:
    """[Multiplayer Card Selection] Select or deselect a card in the card selection screen.

    Args:
        card_index: 0-based index of the card.
    """
    try:
        return await _mp_post({"action": "select_card", "index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_deck_confirm_selection() -> str:
    """[Multiplayer Card Selection] Confirm the current card selection."""
    try:
        return await _mp_post({"action": "confirm_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_deck_cancel_selection() -> str:
    """[Multiplayer Card Selection] Cancel the current card selection."""
    try:
        return await _mp_post({"action": "cancel_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_bundle_select(bundle_index: int) -> str:
    """[Multiplayer Bundle Selection] Open a bundle preview.

    Args:
        bundle_index: 0-based index of the bundle.
    """
    try:
        return await _mp_post({"action": "select_bundle", "index": bundle_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_bundle_confirm_selection() -> str:
    """[Multiplayer Bundle Selection] Confirm the currently previewed bundle."""
    try:
        return await _mp_post({"action": "confirm_bundle_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_bundle_cancel_selection() -> str:
    """[Multiplayer Bundle Selection] Cancel the current bundle preview."""
    try:
        return await _mp_post({"action": "cancel_bundle_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_select_card(card_index: int) -> str:
    """[Multiplayer Combat Selection] Select a card from hand during in-combat card selection.

    Args:
        card_index: 0-based index of the card in the selectable hand cards.
    """
    try:
        return await _mp_post({"action": "combat_select_card", "card_index": card_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_combat_confirm_selection() -> str:
    """[Multiplayer Combat Selection] Confirm the in-combat card selection."""
    try:
        return await _mp_post({"action": "combat_confirm_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_relic_select(relic_index: int) -> str:
    """[Multiplayer Relic Selection] Select a relic (boss relic rewards).

    Args:
        relic_index: 0-based index of the relic.
    """
    try:
        return await _mp_post({"action": "select_relic", "index": relic_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_relic_skip() -> str:
    """[Multiplayer Relic Selection] Skip the relic selection."""
    try:
        return await _mp_post({"action": "skip_relic_selection"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_treasure_claim_relic(relic_index: int) -> str:
    """[Multiplayer Treasure] Bid on / claim a relic from the treasure chest.

    In multiplayer, this is a bid — if multiple players pick the same relic,
    a "relic fight" determines the winner. Others get consolation prizes.

    Args:
        relic_index: 0-based index of the relic.
    """
    try:
        return await _mp_post({"action": "claim_treasure_relic", "index": relic_index})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_crystal_sphere_set_tool(tool: str) -> str:
    """[Multiplayer Crystal Sphere] Switch the active divination tool.

    Args:
        tool: Either "big" or "small".
    """
    try:
        return await _mp_post({"action": "crystal_sphere_set_tool", "tool": tool})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_crystal_sphere_click_cell(x: int, y: int) -> str:
    """[Multiplayer Crystal Sphere] Click a hidden cell on the Crystal Sphere grid.

    Args:
        x: Cell x-coordinate.
        y: Cell y-coordinate.
    """
    try:
        return await _mp_post({"action": "crystal_sphere_click_cell", "x": x, "y": y})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def mp_crystal_sphere_proceed() -> str:
    """[Multiplayer Crystal Sphere] Continue after the Crystal Sphere minigame finishes."""
    try:
        return await _mp_post({"action": "crystal_sphere_proceed"})
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def start_recording(
    fps: int = 15, max_duration_seconds: int = 300,
    width: int = 1280, height: int = 720,
    audio: bool = False,
) -> str:
    """Record the game viewport to H.264 MP4, optionally with game audio.

    Works in menus, singleplayer and multiplayer. Requires FFmpeg with libx264
    on the game's PATH (or STS2_MCP_FFMPEG). Only one recording can run at once.
    fps: 1-30. max_duration_seconds: 1-3600; stops automatically at this limit.
    width/height: even integers, up to 1920/1080. Preserves aspect ratio.
    audio: False by default. True records game-process audio as AAC (no mic or
        other apps), requiring Windows build 20348+ (including Windows 11).
        Muted game audio records silence. Audio muxing occurs after capture stops.
    Returns output_path and initial status; poll get_recording_status for errors.
    """
    try:
        r = await _get_client().post(f"{_base_url}/api/v1/recording/start", json={
            "fps": fps, "max_duration_seconds": max_duration_seconds,
            "width": width, "height": height,
            "audio": audio,
        })
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def get_recording_status() -> str:
    """Get recording status, local output path, actual capture FPS and errors.

    status: idle, recording, stopping, completed or failed. Only completed files
    are ready to use; paths refer to the game machine, not the MCP client.
    capture_fps and frames_repeated reveal slow capture hidden by nominal FPS.
    """
    try:
        r = await _get_client().get(f"{_base_url}/api/v1/recording")
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def stop_recording() -> str:
    """Stop recording and begin MP4 finalization; safe to call repeatedly.

    Returns immediately. Poll get_recording_status until completed or failed
    before opening the file or starting another recording.
    """
    try:
        r = await _get_client().post(f"{_base_url}/api/v1/recording/stop")
        r.raise_for_status()
        return r.text
    except Exception as e:
        return _handle_error(e)


def main():
    parser = argparse.ArgumentParser(description="Karen STS2 MCP Server")
    parser.add_argument("--port", type=int, default=15527, help="Game HTTP server port")
    parser.add_argument("--host", type=str, default="localhost", help="Game HTTP server host")
    parser.add_argument("--no-trust-env", action="store_true", help="Ignore HTTP_PROXY/HTTPS_PROXY environment variables")
    args = parser.parse_args()

    global _base_url, _trust_env
    _base_url = f"http://{args.host}:{args.port}"
    _trust_env = not args.no_trust_env

    # Eagerly initialize the shared httpx client so the first request is fast
    _get_client()

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
