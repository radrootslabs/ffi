package org.radroots

object Radroots {
    @JvmField val NAME: String = org.radroots.internal.name()

    @JvmStatic fun name(): String = org.radroots.internal.name()

    @JvmStatic
    fun printName() {
        org.radroots.internal.printName()
    }
}
